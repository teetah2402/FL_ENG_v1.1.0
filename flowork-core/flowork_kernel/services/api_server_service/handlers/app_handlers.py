########################################################################
# WEBSITE https://flowork.cloud
# File NAME : C:\flowork-nano\flowork-core\flowork_kernel\services\api_server_service\handlers\app_handlers.py total lines 205 
########################################################################

import asyncio
import json
import sys
import importlib.util
from aiohttp import web
from flowork_kernel.utils.path_helper import get_apps_directory

class AppHandlersMixin:

    async def handle_list_apps(self, request):
        try:
            manager = getattr(self, "app_manager_service", None)

            if not manager or not hasattr(manager, 'list_apps'):
                 lifecycle_svc = self.kernel.get_service("app_lifecycle_service")
                 if not lifecycle_svc or not hasattr(lifecycle_svc, 'loaded_apps'):
                    return web.json_response([], status=200)
                 apps_map = lifecycle_svc.loaded_apps
            else:
                 apps_map = manager.list_apps()

            apps_list = []
            for app_id, instance in apps_map.items():
                app_info = {
                    "id": app_id,
                    "name": getattr(instance, "name", app_id),
                    "status": "active"
                }
                try:
                    manifest_path = get_apps_directory() / app_id / "manifest.json"
                    if manifest_path.exists():
                        with open(manifest_path, 'r') as f:
                            manifest = json.load(f)
                            app_info.update(manifest)
                except: pass

                apps_list.append(app_info)

            return web.json_response(apps_list)
        except Exception as e:
            self.kernel.write_to_log(f"List Apps Error: {e}", "ERROR")
            return web.json_response({"error": str(e)}, status=500)

    async def handle_list_app_actions(self, request):
        app_id = request.match_info.get("app_id")
        try:
            lifecycle_svc = self.kernel.get_service("app_lifecycle_service")
            if not lifecycle_svc or not hasattr(lifecycle_svc, 'loaded_apps'):
                return web.json_response({"error": "App Factory not ready"}, status=503)

            app_service = lifecycle_svc.loaded_apps.get(app_id)
            if not app_service:
                return web.json_response({"error": "App not found"}, status=404)

            if not hasattr(app_service, 'router'):
                 try:
                     apps_dir = get_apps_directory()
                     router_path = apps_dir / app_id / "backend" / "router.py"

                     if not router_path.exists():
                         return web.json_response({"actions": []})

                     spec = importlib.util.spec_from_file_location(f"apps.{app_id}.router", str(router_path))
                     module = importlib.util.module_from_spec(spec)
                     sys.modules[f"apps.{app_id}.router"] = module
                     spec.loader.exec_module(module)

                     app_service.router = module.AppRouter(app_service)
                 except Exception as e:
                     return web.json_response({"error": f"Router Init Failed: {e}"}, status=500)

            routes = app_service.router.get_routes()
            actions_list = []
            for action_name, func in routes.items():
                actions_list.append({
                    "name": action_name,
                    "description": func.__doc__.strip() if func.__doc__ else "No description",
                })

            return web.json_response({"app_id": app_id, "actions": actions_list})

        except Exception as e:
            self.kernel.write_to_log(f"List Actions Error: {e}", "ERROR")
            return web.json_response({"error": str(e)}, status=500)

    async def handle_get_app_asset(self, request):
        app_id = request.match_info.get("app_id")
        filename = request.match_info.get("filename")

        try:
            apps_dir = get_apps_directory()
            file_path = apps_dir / app_id / filename

            if not file_path.exists():
                file_path = apps_dir / app_id / "assets" / filename

            if not file_path.exists():
                return web.Response(status=404, text="Asset not found")

            return web.FileResponse(file_path)

        except Exception as e:
            self.kernel.write_to_log(f"Asset Error: {e}", "ERROR")
            return web.Response(status=500, text=str(e))

    async def handle_list_app_nodes(self, request):
        try:
            apps_dir = get_apps_directory()
            available_nodes = []

            if apps_dir.exists():
                for app_folder in apps_dir.iterdir():
                    manifest_path = app_folder / "manifest.json"
                    if manifest_path.exists():
                        try:
                            with open(manifest_path, 'r') as f:
                                data = json.load(f)
                                if "workflow_node" in data.get("capabilities", []):
                                    node_def = data.get("node_spec", {})
                                    node_def["app_id"] = data["id"]
                                    node_def["icon_url"] = f"/api/v1/apps/{data['id']}/icon"
                                    available_nodes.append(node_def)
                        except Exception as e:
                            self.kernel.write_to_log(f"Manifest Read Error ({app_folder.name}): {e}", "WARN")

            return web.json_response({"nodes": available_nodes})
        except Exception as e:
            self.kernel.write_to_log(f"Node Discovery Error: {e}", "ERROR")
            return web.json_response({"error": str(e)}, status=500)


    async def handle_app_execute(self, request):
        app_id = request.match_info.get("app_id")
        action = request.match_info.get("action")

        try:
            lifecycle_svc = self.kernel.get_service("app_lifecycle_service")

            if not lifecycle_svc:
                return web.json_response({"error": "App Factory Service not running"}, status=503)

            if not hasattr(lifecycle_svc, 'loaded_apps'):
                 lifecycle_svc.loaded_apps = {}

            app_service = lifecycle_svc.loaded_apps.get(app_id)

            if not app_service:
                return web.json_response({"error": f"App '{app_id}' not found or offline."}, status=404)

            if not hasattr(app_service, 'router'):
                 try:
                     apps_dir = get_apps_directory()
                     router_path = apps_dir / app_id / "backend" / "router.py"

                     if not router_path.exists():
                         return web.json_response({"error": f"Router file not found at {router_path}"}, status=501)

                     spec = importlib.util.spec_from_file_location(f"apps.{app_id}.router", str(router_path))
                     module = importlib.util.module_from_spec(spec)
                     sys.modules[f"apps.{app_id}.router"] = module
                     spec.loader.exec_module(module)

                     app_service.router = module.AppRouter(app_service)

                 except Exception as e:
                     import traceback
                     self.kernel.write_to_log(f"Router Load Error: {traceback.format_exc()}", "ERROR")
                     return web.json_response({"error": f"Router Init Failed: {e}"}, status=500)

            routes = app_service.router.get_routes()
            if action not in routes:
                return web.json_response({"error": f"Action '{action}' not found in App '{app_id}'"}, status=400)

            payload = {}
            if request.can_read_body:
                try:
                    payload = await request.json()
                except: pass

            if "user_context" not in payload:
                 user_id = request.headers.get("X-Flowork-User-ID", "system")
                 payload["user_context"] = {"user_id": user_id}

            handler_func = routes[action]

            if asyncio.iscoroutinefunction(handler_func):
                result = await handler_func(payload)
            else:
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(None, handler_func, payload)

            if isinstance(result, web.StreamResponse):
                return result

            return web.json_response(result)

        except Exception as e:
            self.kernel.write_to_log(f"App Execution Error for {app_id}: {e}", "ERROR")
            return web.json_response({"error": "App Execution Failed", "details": str(e)}, status=500)
