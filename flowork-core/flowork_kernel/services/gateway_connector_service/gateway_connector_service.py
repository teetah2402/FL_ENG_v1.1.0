########################################################################
# WEBSITE https://flowork.cloud
# File NAME : C:\flowork-nano\flowork-core\flowork_kernel\services\gateway_connector_service\gateway_connector_service.py total lines 444 
########################################################################

import socketio
import os
import asyncio
import logging
import uuid
import json
import multiprocessing
import requests
import time
import sqlite3
from dotenv import load_dotenv
from typing import Dict, Any
from flowork_kernel.services.base_service import BaseService
from flowork_kernel.singleton import Singleton
from flowork_kernel.services.database_service.database_service import DatabaseService
from flowork_kernel.services.variable_manager_service.variable_manager_service import VariableManagerService
from flowork_kernel.exceptions import PermissionDeniedError

from .handlers.system_handler import SystemHandler
from .handlers.workflow_handler import WorkflowHandler
from .handlers.data_handler import DataHandler

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '..', '..', '.env'))
CURRENT_PAYLOAD_VERSION = 2

class GatewayConnectorService(BaseService):
    def __init__(self, kernel, service_id):
        super().__init__(kernel, service_id)
        self.sio = socketio.AsyncClient(
            logger=True,
            engineio_logger=False,
            reconnection=True,
            reconnection_delay=5,
            reconnection_attempts=0
        )
        self.gateway_url = os.getenv("GATEWAY_API_URL", "http://gateway:8000")
        self.engine_token = os.getenv("FLOWORK_ENGINE_TOKEN")
        self.engine_id = os.getenv("FLOWORK_ENGINE_ID")
        self.kernel_services = {}
        self.user_id = None
        self.internal_api_url = None
        self._hb_task = None
        self._watchdog_task = None
        self._poller_task = None

        self._loop = None


        self._pending_swarm_tasks: Dict[str, asyncio.Future] = {}
        self._pending_swarm_tasks_lock = asyncio.Lock()


        if not hasattr(self.kernel, "memory_store"):
            self.kernel.memory_store = {}

        self.logger.info(f"GatewayConnectorService (Lite Mode) initialized. URL: {self.gateway_url}")

        self.handlers = [
            SystemHandler(self),
            WorkflowHandler(self),
            DataHandler(self),
        ]
        self.register_event_handlers()

    async def _event_poller(self):
        """
        [FIX] Scrapes DB for events left by Workers using ID tracking (Timezone-safe).
        """
        self.logger.info("[GatewayConnector] 🕵️ Event Rescue Poller started (Set-Based).")
        db_path = os.path.join(self.kernel.data_path if hasattr(self.kernel, 'data_path') else '/app/data', "flowork_core.db")

        processed_jobs = set()

        while True:
            try:
                if not os.path.exists(db_path):
                    await asyncio.sleep(2)
                    continue

                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()

                cursor.execute("""
                    SELECT job_id, output_data, user_id
                    FROM Jobs
                    WHERE status = 'DONE'
                    AND output_data LIKE '%__emit_events%'
                    ORDER BY finished_at DESC
                    LIMIT 50
                """)

                rows = cursor.fetchall()
                conn.close()

                for row in rows:
                    job_id, output_json, user_id = row

                    if job_id in processed_jobs:
                        continue

                    processed_jobs.add(job_id)

                    if len(processed_jobs) > 2000:
                        processed_jobs = set(list(processed_jobs)[-1000:])

                    try:
                        output = json.loads(output_json)
                        events = output.get("__emit_events", [])

                        if events:
                            self.logger.info(f"[EventPoller] 🎁 Found {len(events)} events in Job {job_id}")

                        for evt in events:
                            evt_name = evt.get("event")
                            evt_payload = evt.get("payload")

                            if user_id and isinstance(evt_payload, dict):
                                evt_payload['_target_user_id'] = user_id

                            self.logger.info(f"[EventPoller] 🚀 Rescuing & Emitting '{evt_name}'")

                            await self.forward_event_to_gateway_async(evt_name, "poller", evt_payload)

                    except (json.JSONDecodeError, TypeError):
                        pass

            except Exception as e:
                self.logger.error(f"[EventPoller] Error: {e}")

            await asyncio.sleep(0.5)

    async def _run_watchdog(self):
        self.logger.info("[Watchdog] Active Connection Stabilizer STARTED (Interval: 5s).")
        try:
            while True:
                if self.sio.connected:
                    try:
                        await self.sio.emit('core:ping', {'ts': int(time.time()), 'engine_id': self.engine_id}, namespace='/engine-socket')
                    except Exception as e:
                        self.logger.warning(f"[Watchdog] Ping failed (Connection unstable?): {e}")
                else:
                    self.logger.debug("[Watchdog] Socket disconnected. Waiting for auto-reconnect...")

                await asyncio.sleep(5)

        except asyncio.CancelledError:
            self.logger.info("[Watchdog] Task Cancelled.")
        except Exception as e:
            self.logger.error(f"[Watchdog] CRITICAL FAILURE: {e}", exc_info=True)

    async def send_gateway_swarm_task(self, target_engine_id: str, task_payload: Dict[str, Any]) -> Dict[str, Any]:
        task_id = task_payload.get("task_id")
        if not task_id:
            return {"error": "send_gateway_swarm_task: task_payload must have a 'task_id'."}

        if not self.sio.connected:
            self.logger.error(f"[Gateway R6] Cannot send task {task_id}: Socket not connected.")
            return {"error": "GatewayError: Core is not connected to Gateway."}

        loop = asyncio.get_running_loop()
        task_future = loop.create_future()

        async with self._pending_swarm_tasks_lock:
            self._pending_swarm_tasks[task_id] = task_future

        self.logger.info(f"[Gateway R6] Sending swarm task {task_id} to Gateway (Target: {target_engine_id})...")

        try:
            await self.emit_to_gateway('core:request_swarm_task', {
                "target_engine_id": target_engine_id,
                "task_payload": task_payload
            })

            timeout_s = task_payload.get("swarm_timeout_s", 30.0)

            result = await asyncio.wait_for(task_future, timeout=timeout_s)
            self.logger.info(f"[Gateway R6] Received result for task {task_id}.")
            return result

        except asyncio.TimeoutError:
            self.logger.error(f"[Gateway R6] Task {task_id} timed out waiting for Gateway result.")
            return {"error": f"GatewayTimeout: Task {task_id} timed out after {timeout_s}s."}
        except Exception as e:
            self.logger.error(f"[Gateway R6] Failed to send/wait for task {task_id}: {e}", exc_info=True)
            return {"error": f"GatewayError: Failed to send task: {e}"}
        finally:
            async with self._pending_swarm_tasks_lock:
                self._pending_swarm_tasks.pop(task_id, None)

    def _resolve_home_gateway(self) -> str:
        default_url = self.gateway_url.rstrip('/')

        if "gateway" in default_url or "localhost" in default_url or "127.0.0.1" in default_url:
             self.logger.info(f"[GatewayConnector] Local/Docker environment detected. Skipping resolution. Using: {default_url}")
             return default_url

        try:
            resolver_url = f"{default_url}/api/v1/cluster/resolve-home?key={self.engine_id}"
            self.logger.info(f"[GatewayConnector] Resolving home gateway via: {resolver_url}")
            res = requests.get(resolver_url, timeout=3.0)

            if res.status_code == 200:
                data = res.json()
                home_url = data.get("home_url")
                if home_url:
                    self.logger.info(f"[GatewayConnector] Home gateway resolved to: {home_url}")
                    return home_url.rstrip('/')

            self.logger.warning(f"[GatewayConnector] Resolver returned non-200 or empty. Using default.")
            return default_url

        except Exception as e:
            self.logger.warning(f"[GatewayConnector] Resolution failed ({str(e)}). Using fallback: {default_url}")
            return default_url

    def set_kernel_services(self, kernel_services: dict):
        self.kernel_services = kernel_services
        self.logger.info(f"Kernel services injected. {len(self.kernel_services)} services loaded.")

        event_bus = self.kernel_services.get("event_bus")
        if event_bus:
            self.logger.info("[GatewayConnector] Subscribing to main event bus for GUI forwarding.")
            event_bus.subscribe("*", "gateway_gui_forwarder", self.forward_event_to_gateway_sync_wrapper)

            self.logger.info("[GatewayConnector] Subscribing to HYBRID_ACTION_REQUEST for Bridge.")
            event_bus.subscribe("HYBRID_ACTION_REQUEST", "gateway_hybrid_bridge", self.on_hybrid_request_internal_sync_wrapper)
        else:
            self.logger.error("[GatewayConnector] EventBus not found in kernel_services. GUI forwarding will fail.")

    async def emit_to_gateway(self, event_name: str, payload: dict):
        try:
            if not self.sio.connected:
                return

            if event_name not in ['core:agent_token', 'core:ping', 'engine_vitals_update']:
                self.logger.info(f"[Core Emitter] Sending '{event_name}' to Gateway.")

            await self.sio.emit(event_name, payload, namespace='/engine-socket')

        except Exception as e:
            self.logger.error(f"[Core Emitter] Failed to emit '{event_name}': {e}", exc_info=True)

    def forward_event_to_gateway_sync_wrapper(self, event_name, subscriber_id, payload):
        if self._loop and self._loop.is_running():
            asyncio.run_coroutine_threadsafe(
                self.forward_event_to_gateway_async(event_name, subscriber_id, payload),
                self._loop
            )

    async def forward_event_to_gateway_async(self, event_name, subscriber_id, payload):
        try:
            if not self.sio.connected:
                return

            GUI_SAFE_EVENTS = [
                "SHOW_DEBUG_POPUP",
                "WORKFLOW_EXECUTION_UPDATE",
                "NODE_METRIC_UPDATE",
                "WORKFLOW_LOG_ENTRY",
                "JOB_COMPLETED_CHECK",
                "APPS_RELOADED",
                "WIDGETS_RELOADED",
                "COMPONENT_LIST_CHANGED"
            ]

            if event_name in GUI_SAFE_EVENTS:
                target_user_id = self.user_id
                if isinstance(payload, dict) and '_target_user_id' in payload:
                    target_user_id = payload.get('_target_user_id')

                versioned_payload = {
                    'v': CURRENT_PAYLOAD_VERSION,
                    'payload': {
                        'event_name': event_name,
                        'event_data': payload,
                        'user_id': target_user_id
                    }
                }

                await self.sio.emit('forward_event_to_gui', versioned_payload, namespace='/engine-socket')

        except Exception as e:
            self.logger.error(f"[GatewayConnector] Error forwarding event '{event_name}': {e}", exc_info=True)

    forward_event_to_gateway = forward_event_to_gateway_sync_wrapper

    def on_hybrid_request_internal_sync_wrapper(self, event_name, subscriber_id, payload):
        if self._loop and self._loop.is_running():
            asyncio.run_coroutine_threadsafe(
                self.on_hybrid_request_internal_async(event_name, subscriber_id, payload),
                self._loop
            )
        else:
            self.logger.warning("[GatewayConnector] Event loop not ready for Hybrid Request.")

    async def on_hybrid_request_internal_async(self, event_name, subscriber_id, payload):
        self.logger.info(f"📤 [Bridge] Relaying Request to Gateway: {payload.get('action')}")

        if self.sio.connected:
            try:
                await self.sio.emit('app_action_request', payload, namespace='/engine-socket')
            except Exception as e:
                self.logger.error(f"❌ [Bridge] Failed to emit: {e}")
        else:
            self.logger.warning("⚠️ [Bridge] Cannot relay request: Gateway disconnected.")

    async def on_hybrid_response(self, data):
        request_id = data.get('request_id')
        status = data.get('status')
        result_data = data.get('data')
        error_msg = data.get('error')

        self.logger.info(f"📥 [Bridge] Received Response from Frontend: ID={request_id} Status={status}")

        if request_id:
            response_key = f"response_{request_id}"
            value = result_data if status == 'success' else {"error": error_msg}
            self.kernel.memory_store[response_key] = value

    def _get_safe_roots(self):
        roots = [os.path.abspath(self.kernel.project_root_path)]
        user_home = os.path.expanduser('~')
        common_dirs = ['Desktop', 'Documents', 'Downloads', 'Pictures', 'Music', 'Videos']
        for d in common_dirs:
            path = os.path.join(user_home, d)
            if os.path.isdir(path):
                roots.append(os.path.abspath(path))
        return sorted(list(set(roots)))

    def register_event_handlers(self):
        for handler in self.handlers:
            handler.register_events()
            self.logger.info(f"Registered events from handler: {handler.__class__.__name__}")

    async def _engine_heartbeat(self):
        self.logger.info("[GatewayConnector] Heartbeat task started.")
        try:
            while True:
                try:
                    cpu_usage = psutil.cpu_percent(interval=None) if PSUTIL_AVAILABLE else 0
                    mem_percent = 0
                    if PSUTIL_AVAILABLE:
                         mem = psutil.virtual_memory()
                         mem_percent = mem.percent

                    payload = {
                        'engine_id': self.engine_id,
                        'user_id': self.user_id,
                        'internal_api_url': self.internal_api_url,
                        'ts': int(time.time()),
                        'cpu_percent': cpu_usage,
                        'memory_percent': mem_percent,
                        'metrics': {
                            'pid': os.getpid(),
                            'active_fac_sessions': 0, # [REMOVED FAC]
                            'cpuPercent': cpu_usage,
                            'memoryPercent': mem_percent
                        }
                    }

                    await self.sio.emit('engine_vitals_update', payload, namespace='/engine-socket')
                except Exception as e:
                    self.logger.debug(f"[GatewayConnector] Heartbeat skipped: {e}")
                await asyncio.sleep(10)
        except asyncio.CancelledError:
            self.logger.info("[GatewayConnector] Heartbeat task cancelled.")
        except Exception as e:
            self.logger.error(f"[GatewayConnector] Heartbeat task crashed: {e}", exc_info=True)

    async def start(self):
        if not self.engine_id or not self.engine_token or not self.gateway_url:
            self.logger.error("GatewayConnectorService not properly set up. Missing URL, Engine ID or Token.")
            return

        self._loop = asyncio.get_running_loop()

        resolved_http_url = self._resolve_home_gateway()

        if resolved_http_url.startswith("https://"):
            connect_url = resolved_http_url.replace("https://", "wss://")
        else:
            connect_url = resolved_http_url.replace("http://", "ws://")

        socketio_path = "/api/socket.io"
        self.logger.info(f"[GatewayConnector] Connecting to WebSocket at: {connect_url} with path {socketio_path}")

        auth_payload = {
            'engine_id': self.engine_id,
            'token': self.engine_token
        }

        self.sio.on('app_action_response', self.on_hybrid_response, namespace='/engine-socket')

        while True:
            try:
                await self.sio.connect(
                    connect_url,
                    headers={"Authorization": f"Bearer {self.engine_token}"},
                    auth=auth_payload,
                    namespaces=['/engine-socket'],
                    socketio_path=socketio_path
                )
                self.logger.info(f"[GatewayConnector] Initial connection successful to {connect_url}")

                self._hb_task = self._loop.create_task(self._engine_heartbeat())
                self._watchdog_task = self._loop.create_task(self._run_watchdog())
                self._poller_task = self._loop.create_task(self._event_poller())

                await self.sio.wait()

            except socketio.exceptions.ConnectionError as e:
                self.logger.error(f"Failed to connect to Gateway at {connect_url}: {e}. Retrying in 5 seconds...")
            except Exception as e:
                self.logger.error(f"An unexpected error occurred in GatewayConnectorService: {e}", exc_info=True)
            finally:
                self.logger.info("GatewayConnectorService stopped. Will attempt to restart connection loop.")
                await asyncio.sleep(5)

    async def stop(self):
        self.logger.info("Stopping GatewayConnectorService...")
        try:
            if self._hb_task and not self._hb_task.done():
                self._hb_task.cancel()
            if self._watchdog_task and not self._watchdog_task.done():
                self._watchdog_task.cancel()
            if self._poller_task and not self._poller_task.done():
                self._poller_task.cancel()

            if self.sio.connected:
                await self.sio.disconnect()
        except Exception as e:
            self.logger.error(f"Error during disconnect: {e}", exc_info=True)
