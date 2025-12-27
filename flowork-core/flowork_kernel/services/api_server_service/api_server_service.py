########################################################################
# WEBSITE https://flowork.cloud
# File NAME : C:\flowork-nano\flowork-core\flowork_kernel\services\api_server_service\api_server_service.py total lines 265 
########################################################################

import asyncio
from aiohttp import web
import threading
import os
import importlib
import inspect
import sys
import importlib.util
import functools
from collections import deque
from urllib.parse import urlparse, unquote

from ..base_service import BaseService
from .routes.base_api_route import BaseApiRoute
from flowork_kernel.utils.tracing_setup import setup_tracing

from .dependencies import DependenciesMixin
from .middleware import MiddlewareMixin
from .executors import ExecutorMixin
from .handlers.app_handlers import AppHandlersMixin
from .handlers.system_handlers import SystemHandlersMixin
from .handlers.webhook_handlers import WebhookHandlersMixin

from .routes.filesystem_routes import FilesystemRoutes
from .routes.engine_routes import EngineRoutes
from .routes.preset_routes import PresetRoutes

class ApiServerService(
    BaseService,
    DependenciesMixin,
    MiddlewareMixin,
    ExecutorMixin,
    AppHandlersMixin,
    SystemHandlersMixin,
    WebhookHandlersMixin
):
    def __init__(self, kernel, service_id: str):
        BaseService.__init__(self, kernel, service_id)
        self.tracer = setup_tracing(service_name="flowork-core")
        self.job_statuses = {}
        self.job_statuses_lock = threading.Lock()
        self.recent_events = deque(maxlen=15)
        self.kernel.write_to_log("Service 'ApiServerService' initialized.", "DEBUG")
        self.core_component_ids = None

        self.variable_manager = None
        self.preset_manager = None
        self.state_manager = None
        self.app_manager_service = None
        self.ai_provider_manager_service = None
        self.db_service = None
        self.prompt_manager_service = None
        self.event_bus = None
        self.workflow_executor = None
        self.metrics_service = None


        self.app = None
        self.runner = None
        self.site = None

    async def start(self):
        self._load_dependencies()
        self.app = web.Application(middlewares=[self.middleware_handler])
        self._load_api_routes()
        self.core_component_ids = await self._load_protected_component_ids()

        if hasattr(self, 'loc') and self.loc:
             port = self.loc.get_setting("webhook_port", 8989)
        else:
             port = 8989 # Fallback default port

        host = "0.0.0.0"
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
        self.site = web.TCPSite(self.runner, host, port)
        try:
            await self.site.start()

            startup_msg = "ApiServer: Now running on a high-performance asynchronous core (AIOHTTP)."
            if hasattr(self, 'loc') and self.loc:
                startup_msg = self.loc.get("log_startup_async_server", fallback=startup_msg)

            self.kernel.write_to_log(startup_msg, "SUCCESS")

            self.kernel.write_to_log(
                f"API server (Asynchronous) started and listening at http://{host}:{port}",
                "SUCCESS",
            )
        except OSError as e:
            if "address already in use" in str(e).lower():
                self.kernel.write_to_log(
                    f"FATAL: API server port {port} is already in use. Another instance running or port blocked?",
                    "CRITICAL"
                )
            else:
                self.kernel.write_to_log(
                    f"FATAL: Could not start API server on port {port}: {e}",
                    "CRITICAL"
                )
            import sys
            sys.exit(1)
        except Exception as e:
            self.kernel.write_to_log(
                f"FATAL: Unexpected error starting API server: {e}",
                "CRITICAL"
            )
            import sys
            sys.exit(1)

    def _load_api_routes(self):
        self.kernel.write_to_log(
            "ApiServer: Discovering and loading API routes...", "INFO"
        )

        all_route_classes = [
            FilesystemRoutes,
            EngineRoutes,
            PresetRoutes,
        ]

        routes_dir = os.path.join(os.path.dirname(__file__), "routes")
        for filename in os.listdir(routes_dir):
            if (
                filename.endswith((".py", ".service"))
                and not filename.startswith("__")
                and "base_api_route" not in filename
                and "filesystem_routes" not in filename
                and "engine_routes" not in filename
                and "preset_routes" not in filename
                and "dataset_routes" not in filename
                and "training_routes" not in filename
                and "model_routes" not in filename
                and "neural_ingestor_routes" not in filename
                and "license_routes" not in filename # REMOVED: Web3 Open Core
                and "agent_routes" not in filename # REMOVED: Bloatware
                and "recorder_routes" not in filename # REMOVED: Bloatware
                and "component_routes" not in filename # REMOVED: Uses legacy managers
                and "ui_state_routes" not in filename # REMOVED: Often uses license
            ):
                module_base_name = os.path.splitext(filename)[0]
                module_name = f"flowork_kernel.services.api_server_service.routes.{module_base_name}"
                try:
                    module_file_path = os.path.join(routes_dir, filename)
                    spec = importlib.util.spec_from_file_location(module_name, module_file_path)
                    if spec is None:
                        self.kernel.write_to_log(f"Could not create module spec from {module_file_path}", "ERROR")
                        continue
                    module = importlib.util.module_from_spec(spec)
                    sys.modules[module_name] = module
                    spec.loader.exec_module(module)
                    for name, obj in inspect.getmembers(module, inspect.isclass):
                        if issubclass(obj, BaseApiRoute) and obj is not BaseApiRoute:
                            if obj not in all_route_classes:
                                all_route_classes.append(obj)
                except Exception as e:
                    self.kernel.write_to_log(
                        f"Failed to discover routes from {filename}: {e}", "ERROR"
                    )

        for route_class in all_route_classes:
            try:
                self.kernel.write_to_log(
                    f"  -> Loading routes from: {route_class.__name__}", "DEBUG"
                )
                route_instance = route_class(self)
                registered_routes = route_instance.register_routes()
                for route, handler in registered_routes.items():
                    method, pattern = route.split(" ", 1)
                    if not asyncio.iscoroutinefunction(handler):
                         self.app.router.add_route(method, pattern, handler)
                    else:
                        self.app.router.add_route(method, pattern, handler)
            except Exception as e:
                import traceback
                self.kernel.write_to_log(
                    f"Failed to load routes from {route_class.__name__}: {e}\n{traceback.format_exc()}", "ERROR"
                )

        self.kernel.write_to_log("  -> [AWENK BRIDGE] Injecting Service-Level Routes (Lite Mode)...", "INFO")

        class ServiceRouteBridge:
            def __init__(self, app_router, log_func):
                self.router = app_router
                self.log = log_func

            def add_route(self, url, handler, methods=['GET']):
                async def bridged_handler(request):
                    json_body = {}
                    try:
                        if request.can_read_body:
                             json_body = await request.json()
                    except: pass

                    class SyncRequestProxy:
                        def __init__(self, r, j):
                             self.original = r
                             self.json = j
                             self.match_info = r.match_info
                        def __getattr__(self, attr):
                            return getattr(self.original, attr)

                    sync_req = SyncRequestProxy(request, json_body)

                    kwargs = dict(request.match_info)

                    loop = asyncio.get_event_loop()
                    return await loop.run_in_executor(None, functools.partial(handler, sync_req, **kwargs))

                for m in methods:
                    try:
                        resource = self.router.add_resource(url)
                        resource.add_route(m, bridged_handler)
                        self.log(f"    - [BRIDGE] Registered: {m} {url}", "DETAIL")
                    except RuntimeError as re:
                         self.log(f"    - [BRIDGE WARN] Route {url} conflict: {re}. Attempting Force Patch...", "WARN")

        target_services = [
            "ai_provider_manager_service",
        ]

        for service_id in target_services:
            service = self._safe_get_service(service_id)
            if service and hasattr(service, "register_routes"):
                self.kernel.write_to_log(f"  -> Bridging routes for: {service_id}", "DEBUG")
                try:
                    bridge = ServiceRouteBridge(self.app.router, self.kernel.write_to_log)
                    service.register_routes(bridge)
                except Exception as e:
                    self.kernel.write_to_log(f"Bridge failed for {service_id}: {e}", "ERROR")

        async def health_check(request):
            status = "ready"
            app_mgr = self._safe_get_service("app_manager_service")
            if app_mgr and hasattr(app_mgr, "apps") and len(app_mgr.apps) == 0:
                status = "initializing"

            return web.json_response({
                "status": status,
                "engine_id": os.getenv("FLOWORK_ENGINE_ID"),
                "version": "3.0-LITE"
            })

        self.app.router.add_get("/health", health_check)

        self.app.router.add_post("/api/v1/apps/execute/{app_id}/{action}", self.handle_app_execute)
        self.app.router.add_get("/api/v1/apps", self.handle_list_apps)
        self.app.router.add_get("/api/v1/apps/{app_id}/actions", self.handle_list_app_actions)
        self.app.router.add_get("/api/v1/apps/{app_id}/assets/{filename}", self.handle_get_app_asset)

        self.app.router.add_get("/api/v1/apps/nodes", self.handle_list_app_nodes)

        self.kernel.write_to_log("API route discovery complete.", "SUCCESS")

    async def stop(self):
        if self.runner:
            self.kernel.write_to_log("Stopping aiohttp server...", "INFO")
            await self.runner.cleanup()
            self.kernel.write_to_log("aiohttp server stopped.", "SUCCESS")
