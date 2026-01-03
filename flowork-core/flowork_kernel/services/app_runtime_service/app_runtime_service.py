########################################################################
# WEBSITE https://flowork.cloud
# File NAME : C:\FLOWORK\flowork-core\flowork_kernel\services\app_runtime_service\app_runtime_service.py total lines 315 
########################################################################

import os
import sys
import json
import time
import socket
import struct
import subprocess
import threading
import asyncio
import queue
import importlib.util
import concurrent.futures
from typing import Dict, Any
from flowork_kernel.services.base_service import BaseService

class AppRuntimeService(BaseService):
    def __init__(self, kernel, service_id):
        super().__init__(kernel, service_id)
        self.active_processes = {} # {pid: subprocess.Popen}
        self.log_queue = queue.Queue(maxsize=10000)
        self.is_running = True

    def start(self):
        self.logger.info("💪 [Muscle] AppRuntime Engine Online. Ready to flex.")
        threading.Thread(target=self._log_monitor_loop, daemon=True).start()

    def stop(self):
        self.is_running = False
        self.logger.info("💪 [Muscle] Shutting down all sub-processes...")
        for pid, proc in self.active_processes.items():
            try:
                proc.terminate()
                try:
                    proc.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    proc.kill()
            except: pass

    def trigger_event_handler(self, app_id: str, action_name: str, payload: dict):
        try:
            loop = None
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                pass

            if loop and loop.is_running():
                loop.create_task(self.execute_service_action(app_id, action_name, payload))
            else:
                threading.Thread(
                    target=lambda: asyncio.run(self.execute_service_action(app_id, action_name, payload)),
                    daemon=True
                ).start()
        except Exception as e:
            self.logger.error(f"❌ [Nervous] Failed to trigger event for {app_id}: {e}")

    async def execute_service_action(self, app_id: str, action_name: str, data: dict, retry_count=0):

        app_manager = self.kernel.get_service("app_manager_service")

        if not app_manager:
             self.logger.error("AppManager not found!")
             return {"status": "error", "error": "AppManager Unavailable"}

        try:
            port = app_manager.ensure_app_running(app_id)
        except Exception as e:
            return {"status": "error", "error": f"Failed to start App Daemon: {str(e)}"}

        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.settimeout(10)

        try:
            loop = asyncio.get_running_loop()

            def socket_transaction():
                client.connect(('127.0.0.1', port))
                payload = json.dumps({"action": action_name, "data": data}).encode('utf-8')
                client.sendall(struct.pack('!I', len(payload)))
                client.sendall(payload)

                header = client.recv(4)
                if not header: raise ConnectionResetError("Empty header")
                length = struct.unpack('!I', header)[0]

                chunks = []
                bytes_recd = 0
                while bytes_recd < length:
                    chunk = client.recv(min(length - bytes_recd, 4096))
                    if not chunk: raise ConnectionResetError("Incomplete body")
                    chunks.append(chunk)
                    bytes_recd += len(chunk)

                response_json = b''.join(chunks).decode('utf-8')
                return json.loads(response_json)

            response = await loop.run_in_executor(None, socket_transaction)
            return response

        except (ConnectionRefusedError, ConnectionResetError, socket.timeout) as e:
            if retry_count < 1:
                self.logger.warning(f"⚠️ [Lazarus] App {app_id} connection failed. Reviving... ({str(e)})")
                app_manager.kill_app(app_id)
                await asyncio.sleep(1)
                return await self.execute_service_action(app_id, action_name, data, retry_count=1)
            else:
                self.logger.error(f"💀 [Lazarus] Failed to revive {app_id} after retry.")
                return {"status": "error", "error": "Service Unavailable (App crashed repeatedly)"}

        except Exception as e:
            return {"status": "error", "error": str(e)}
        finally:
            client.close()

    async def execute_with_timeout(self, func, data, timeout=5):
        loop = asyncio.get_running_loop()
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = loop.run_in_executor(executor, func, data)
                return await asyncio.wait_for(future, timeout=timeout)
        except asyncio.TimeoutError:
            raise Exception("Service Timeout: App merespon terlalu lama!")
        except Exception as e:
            raise e

    def execute_app(self, app_id: str, action: str, params: dict, user_id: str):
        """
        Existing Muscle Mode (One-off Process).
        [PHASE 1 UPDATE] Sekarang menggunakan Global Library Injection.
        """
        app_path = self._find_app_path(app_id)
        if not app_path:
            return {"status": "error", "error": f"App '{app_id}' not found"}

        lib_paths = self._ensure_dependencies_warehouse(app_path, app_id)

        entry_point = os.path.join(app_path, "main.py")
        if not os.path.exists(entry_point):
            return {"status": "error", "error": f"Entry point missing: {entry_point}"}

        payload = {
            "action": action,
            "params": params,
            "user_id": user_id,
            "context": {"kernel_mode": "muscle"}
        }

        env = os.environ.copy()
        env["FLOWORK_PAYLOAD"] = json.dumps(payload)
        env["PYTHONUNBUFFERED"] = "1"

        if lib_paths:
            current_pythonpath = env.get("PYTHONPATH", "")
            new_pythonpath = os.pathsep.join(lib_paths) + os.pathsep + app_path + os.pathsep + current_pythonpath
            env["PYTHONPATH"] = new_pythonpath
            self.logger.info(f"💉 [Muscle] Injected {len(lib_paths)} libraries into PYTHONPATH for {app_id}")

        try:
            python_cmd = "python" if sys.platform == "win32" else "python3"

            proc = subprocess.Popen(
                [python_cmd, entry_point],
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                cwd=app_path
            )

            pid = str(proc.pid)
            self.active_processes[pid] = proc

            threading.Thread(
                target=self._stream_logs,
                args=(proc, app_id, pid, user_id),
                daemon=True
            ).start()

            return {"status": "success", "pid": pid, "message": "App execution started"}

        except Exception as e:
            self.logger.error(f"❌ [Muscle] Failed to launch {app_id}: {e}")
            return {"status": "error", "error": str(e)}

    def _find_app_path(self, app_id):

        app_manager = self.kernel.get_service("app_manager_service")
        if app_manager:
            registry = app_manager.get_registry("apps")
            if app_id in registry:
                return registry[app_id]["path"]

        return None

    def _ensure_dependencies_warehouse(self, app_path, app_id):
        """Menggantikan _install_dependencies lama yang barbar."""
        req_file = os.path.join(app_path, "requirements.txt")
        if not os.path.exists(req_file):
            return []

        lib_manager = self.kernel.get_service("library_manager")
        if lib_manager:
            try:
                return lib_manager.resolve_dependencies(app_id, req_file)
            except Exception as e:
                 self.logger.error(f"❌ [Muscle] Warehouse check failed for {app_id}: {e}")
                 return []

        return []


    def _stream_logs(self, proc, app_id, pid, user_id):
        try:
            for line in iter(proc.stdout.readline, ''):
                if not line: break
                clean_line = line.strip()
                if not clean_line: continue

                self.log_queue.put({
                    "app_id": app_id,
                    "pid": pid,
                    "message": clean_line,
                    "user_id": user_id,
                    "timestamp": time.time()
                })
        except Exception:
            pass
        finally:
            if pid in self.active_processes:
                del self.active_processes[pid]

            try:
                self.kernel.write_to_log(
                    f"###SEQUENCE_COMPLETE###",
                    "SUCCESS",
                    node_id=pid,
                    source=f"APP:{app_id}"
                )
            except: pass

            self.kernel.event_bus.publish("APP_JOB_FINISHED", {
                "app_id": app_id, "pid": pid, "status": "completed", "user_id": user_id
            })

    def _log_monitor_loop(self):
        while self.is_running:
            try:
                log_data = self.log_queue.get(timeout=1)
                msg = log_data["message"]
                app_id = log_data["app_id"]
                user_id = log_data["user_id"]
                pid = log_data.get("pid")


                log_level = "INFO"
                if "❌" in msg or "Error" in msg or "Failure" in msg:
                    log_level = "ERROR"
                elif "✅" in msg or "Success" in msg:
                    log_level = "SUCCESS"

                try:
                    self.kernel.write_to_log(
                        msg,
                        log_level,
                        node_id=pid,
                        source=f"APP:{app_id}"
                    )
                except Exception as e:
                    print(f"⚠️ Log Fallback: {e}")
                    self.kernel.event_bus.publish("EXECUTION_LOG", {
                        "app_id": app_id,
                        "message": msg,
                        "user_id": user_id,
                        "level": log_level,
                        "source": f"APP:{app_id}"
                    })

                if "⚡" in msg:
                    self.kernel.event_bus.publish("APP_PROGRESS", {
                        "app_id": app_id,
                        "raw": msg,
                        "percent": self._extract_percent(msg),
                        "user_id": user_id
                    })

                elif msg.startswith("{") and msg.endswith("}"):
                    try:
                        data = json.loads(msg)
                        self.kernel.event_bus.publish("APP_RESULT", {
                            "app_id": app_id,
                            "data": data,
                            "user_id": user_id
                        })
                    except: pass

                print(f"💪 [Log:{app_id}] {msg}")

            except queue.Empty:
                continue
            except Exception as e:
                print(f"Error in log monitor: {e}")

    def _extract_percent(self, msg):
        try:
            import re
            match = re.search(r"(\d+(\.\d+)?)%", msg)
            if match: return float(match.group(1))
        except: pass
        return 0
