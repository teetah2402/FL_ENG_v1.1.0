########################################################################
# WEBSITE https://flowork.cloud
# File NAME : C:\flowork-nano\flowork-core\flowork_kernel\services\api_server_service\routes\component_routes.py total lines 337 
########################################################################

from .base_api_route import BaseApiRoute
import os
import json
import mimetypes
import zipfile
import io
import base64
import shutil
import threading
from aiohttp import web

class ComponentRoutes(BaseApiRoute):

    def register_routes(self):
        base_routes = [
            "GET /api/v1/{resource_type}",
            "POST /api/v1/{resource_type}",           # Handle Create (Dataset)
            "GET /api/v1/{resource_type}/{item_id}",
            "POST /api/v1/{resource_type}/install",
            "PATCH /api/v1/{resource_type}/{item_id}/state",
            "DELETE /api/v1/{resource_type}/{item_id}",
        ]
        routes = {}

        component_types = [
            "apps",     # V2 Naming (Primary)
            "widgets",  # Legacy Naming (Mapped to Apps)
            "ai_providers",
            "models"
        ]

        for route_pattern in base_routes:
            for comp_type in component_types:
                concrete_route = route_pattern.replace("{resource_type}", comp_type)
                method, pattern = concrete_route.split(" ", 1)

                if method == "POST" and pattern.endswith("/install"):
                    routes[concrete_route] = self.handle_install_components
                elif method == "POST" and not pattern.endswith("/package") and not pattern.endswith("/install-package"):
                    routes[concrete_route] = self.handle_create_component
                elif "state" in pattern:
                    routes[concrete_route] = self.handle_patch_component_state
                elif method == "DELETE":
                    routes[concrete_route] = self.handle_delete_components
                else:
                    routes[concrete_route] = self.handle_get_components

        routes["GET /api/v1/apps/nodes"] = self.handle_get_all_app_nodes
        routes["GET /api/v1/apps/{app_id}/icon-info"] = self.handle_get_app_icon_info

        routes["GET /api/v1/ai_providers/services"] = (
            self.handle_get_ai_provider_services
        )
        routes["GET /api/v1/components/{comp_type}/{item_id}/icon"] = (
            self.handle_get_component_icon
        )

        routes["GET /api/v1/apps/{app_id}/assets/{filename:.*}"] = self.handle_get_app_asset
        routes["GET /api/v1/widgets/{app_id}/assets/{filename:.*}"] = self.handle_get_app_asset

        routes["POST /api/v1/components/package"] = self.handle_package_component
        routes["POST /api/v1/components/install-package"] = self.handle_install_package
        routes["POST /api/v1/components/run"] = self.handle_run_component
        routes["POST /api/v1/components/custom/create"] = self.handle_save_custom_component

        return routes

    async def handle_get_all_app_nodes(self, request):
        """
        (English Hardcode) New endpoint to serve all nodes from all apps for the Designer Toolbox.
        """
        app_man = self.service_instance.kernel.get_service("app_manager_service")
        if not app_man:
            return self._json_response([], status=200)

        nodes = app_man.get_all_nodes()
        return self._json_response(nodes)

    async def handle_get_app_icon_info(self, request):
        """
        (English Hardcode) Helper for Gateway to resolve icon path vs MDI string.
        """
        app_id = request.match_info.get("app_id")
        app_man = self.service_instance.kernel.get_service("app_manager_service")
        if not app_man:
            return self._json_response({"icon_file": "icon.svg"})

        info = app_man.get_app_icon_info(app_id)
        return self._json_response(info)

    async def handle_get_app_asset(self, request):
        app_id = request.match_info.get("app_id")
        filename = request.match_info.get("filename")
        if not app_id or not filename:
            return self._json_response({"error": "Missing app_id or filename"}, status=400)

        manager, error = self._get_manager_for_type("apps")
        if error: return self._json_response({"error": error}, status=503)

        items = self._get_items_from_manager(manager, "apps")
        if app_id not in items:
             return self._json_response({"error": f"App '{app_id}' not found."}, status=404)

        app_data = items[app_id]
        app_path = app_data.get("path") or app_data.get("full_path")
        if not app_path or not os.path.isdir(app_path):
             return self._json_response({"error": "App path invalid."}, status=500)

        target_path = os.path.join(app_path, filename)
        try:
            requested_abspath = os.path.abspath(target_path)
            app_abspath = os.path.abspath(app_path)
            if not requested_abspath.startswith(app_abspath):
                return self._json_response({"error": "Access denied."}, status=403)
        except Exception:
             return self._json_response({"error": "Invalid path."}, status=400)

        if not os.path.exists(requested_abspath) or not os.path.isfile(requested_abspath):
             return self._json_response({"error": "Asset not found."}, status=404)

        return await self._serve_image_file(request, requested_abspath)

    async def handle_get_widget_asset(self, request):
        return await self.handle_get_app_asset(request)

    async def handle_run_component(self, request):
        try:
            body = await request.json()
            executor = self.service_instance.kernel.get_service("workflow_executor_service")
            if not executor: return self._json_response({"error": "Service not available."}, status=503)
            await executor.execute_standalone_node(body)
            return self._json_response({"status": "success", "message": "Execution started."})
        except Exception as e:
            return self._json_response({"error": str(e)}, status=500)

    async def handle_save_custom_component(self, request):
        try:
            body = await request.json()
            comp_id, comp_type = body.get("id"), body.get("type", "module")
            code_content = body.get("code", "")
            manifest_content = body.get("manifest", {})
            requirements_content = body.get("requirements", "")

            if not comp_id or not code_content: return self._json_response({"error": "Missing id/code."}, status=400)

            type_map = {
                "app": "apps",
                "widget": "apps"
            }
            folder_name = type_map.get(comp_type, "apps") # Default changed to apps
            root_path = os.path.abspath(os.path.join(self.kernel.project_root_path, ".."))
            target_parent_dir = os.path.join(root_path, folder_name)

            if not os.path.exists(target_parent_dir):
                target_parent_dir = os.path.join(self.kernel.project_root_path, "flowork_kernel", folder_name)
                os.makedirs(target_parent_dir, exist_ok=True)

            comp_dir = os.path.join(target_parent_dir, comp_id)
            os.makedirs(comp_dir, exist_ok=True)
            entry_point = manifest_content.get("entry_point", "processor.py")

            with open(os.path.join(comp_dir, entry_point), "w", encoding="utf-8") as f: f.write(code_content)
            with open(os.path.join(comp_dir, "manifest.json"), "w", encoding="utf-8") as f: json.dump(manifest_content, f, indent=4)
            if requirements_content:
                with open(os.path.join(comp_dir, "requirements.txt"), "w", encoding="utf-8") as f: f.write(requirements_content)

            manager, _ = self._get_manager_for_type(folder_name)
            if manager:
                install_method = getattr(manager, "install_component_dependencies", getattr(manager, "install_app_dependencies", None))
                if install_method:
                    threading.Thread(target=lambda: install_method(comp_id)).start()

            return self._json_response({"status": "success", "message": f"Component {comp_id} saved."})
        except Exception as e:
            return self._json_response({"error": str(e)}, status=500)

    async def handle_create_component(self, request):
        resource_type = request.match_info.get("resource_type")
        if resource_type == "datasets":
            return self._json_response({"error": "Datasets are disabled in Open Core."}, status=501)
        return self._json_response({"error": "Not supported"}, status=501)

    async def handle_package_component(self, request):
        try:
            body = await request.json()
            comp_type_singular, comp_id = body.get("type"), body.get("id")
            type_map = {
                "app": "apps", "widget": "apps"
            }
            resource_type = type_map.get(comp_type_singular, comp_type_singular + "s")
            manager, error = self._get_manager_for_type(resource_type)
            if error: return self._json_response({"error": error}, status=404)
            items = self._get_items_from_manager(manager, resource_type)
            item_data = items.get(comp_id)
            if not item_data: return self._json_response({"error": "Not found"}, status=404)
            folder_path = item_data.get("path") or item_data.get("full_path")

            buffer = io.BytesIO()
            with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                for root, dirs, files in os.walk(folder_path):
                    dirs[:] = [d for d in dirs if d not in ["__pycache__", ".git", ".venv", "node_modules"]]
                    for file in files:
                        if file.endswith(".pyc"): continue
                        file_path = os.path.join(root, file)
                        zip_file.write(file_path, os.path.relpath(file_path, folder_path))

            return self._json_response({"id": comp_id, "zip_data": base64.b64encode(buffer.getvalue()).decode('utf-8')})
        except Exception as e: return self._json_response({"error": str(e)}, status=500)

    async def handle_install_package(self, request):
        try:
            body = await request.json()
            comp_id, comp_type, zip_b64 = body.get("id"), body.get("type", "module"), body.get("zip_data")
            type_map = {
                "app": "apps", "widget": "apps"
            }
            folder_name = type_map.get(comp_type, "apps")
            target_dir = os.path.join(self.kernel.project_root_path, "..", folder_name, comp_id)
            if os.path.exists(target_dir): shutil.rmtree(target_dir)
            os.makedirs(target_dir, exist_ok=True)
            with zipfile.ZipFile(io.BytesIO(base64.b64decode(zip_b64))) as zf: zf.extractall(target_dir)
            return self._json_response({"status": "success", "path": target_dir})
        except Exception as e: return self._json_response({"error": str(e)}, status=500)

    async def _serve_image_file(self, request, image_path):
        try:
            import aiofiles
            async with aiofiles.open(image_path, "rb") as f:
                image_data = await f.read()
            ct, _ = mimetypes.guess_type(image_path)
            return web.Response(body=image_data, content_type=ct or "application/octet-stream")
        except Exception: return self._json_response({"error": "Serve failed"}, status=500)

    async def handle_get_component_icon(self, request):
        comp_type, item_id = request.match_info.get("comp_type"), request.match_info.get("item_id")
        resource_type = "apps" if "app" in comp_type or "widget" in comp_type else comp_type.rstrip("s") + "s"
        manager, _ = self._get_manager_for_type(resource_type)
        true_root = os.path.abspath(os.path.join(self.kernel.project_root_path, ".."))
        assets_path = os.path.join(true_root, "assets")

        icon_path_found = None
        if manager:
             items = self._get_items_from_manager(manager, resource_type)
             component_data = items.get(item_id)
             if component_data:
                 manifest = component_data.get("manifest", {})
                 icon_fn = manifest.get("icon_file") or manifest.get("gui", {}).get("icon")
                 comp_path = component_data.get("path") or component_data.get("full_path")
                 if icon_fn and comp_path and os.path.isfile(os.path.join(comp_path, icon_fn)):
                     icon_path_found = os.path.join(comp_path, icon_fn)

        if not icon_path_found and "." in item_id:
             app_man = self.service_instance.kernel.get_service("app_manager_service")
             node_def = app_man.get_node_definition(item_id) if app_man else None
             if node_def and node_def.get("icon") and not node_def["icon"].startswith("mdi-"):
                  check_p = os.path.join(node_def["path"], node_def["icon"])
                  if os.path.isfile(check_p): icon_path_found = check_p

        return await self._serve_image_file(request, icon_path_found or os.path.join(assets_path, "default_module.png"))

    async def handle_get_ai_provider_services(self, request):
        manager, error = self._get_manager_for_type("ai_providers")
        if error: return self._json_response({"error": error}, status=503)
        return self._json_response(manager.get_loaded_providers_info())

    def _get_manager_for_type(self, resource_type):
        manager_map = {
            "apps": "app_manager_service",
            "widgets": "app_manager_service",
            "ai_providers": "ai_provider_manager_service",
            "models": "ai_provider_manager_service"
        }
        m_name = manager_map.get(resource_type)
        if not m_name: return None, "Invalid type"
        manager = self.service_instance.kernel.get_service(m_name)
        return (manager, None) if manager else (None, "Service unavailable")

    def _get_items_from_manager(self, manager, resource_type):
        if resource_type == "models": return getattr(manager, "local_models", {})

        if resource_type == "datasets":
            return {}

        items_attr_map = {
            "app_manager_service": "loaded_apps",
            "ai_provider_manager_service": "loaded_providers"
        }
        return getattr(manager, items_attr_map.get(manager.service_id, ""), {})

    async def handle_get_components(self, request):
        resource_type = request.match_info.get("resource_type") or request.path.split("/")[3]
        item_id = request.match_info.get("item_id", None)
        manager, error = self._get_manager_for_type(resource_type)
        if error: return self._json_response([], status=200)

        core_files = await self.service_instance._load_protected_component_ids()
        items = self._get_items_from_manager(manager, resource_type)

        if item_id:
            if item_id in items:
                item_data = items[item_id]
                manifest = item_data.get("manifest", {})
                return self._json_response({"id": item_id, "name": manifest.get("name", item_id), "version": manifest.get("version", "N/A"), "is_paused": item_data.get("is_paused", False), "description": manifest.get("description", ""), "manifest": manifest, "path": item_data.get("path") or item_data.get("full_path")})
            else:
                if resource_type in ["tools", "triggers", "modules"]:
                     app_man = self.service_instance.kernel.get_service("app_manager_service")
                     node_def = app_man.get_node_definition(item_id) if app_man else None
                     if node_def: return self._json_response({"id": item_id, "name": node_def.get("label", item_id), "is_app_node": True, "app_id": node_def.get("app_id"), "manifest": node_def.get("node_def", {})})
                return self._json_response({"error": "Not found"}, status=404)
        else:
            response_data = []
            for id_loop, data in items.items():
                manifest = data.get("manifest", {})
                response_data.append({"id": id_loop, "name": manifest.get("name", id_loop), "version": manifest.get("version", "1.0.0"), "is_paused": data.get("is_paused", False), "description": manifest.get("description", ""), "is_core": id_loop in core_files, "tier": manifest.get("tier", "free"), "manifest": manifest})


            return self._json_response(sorted(response_data, key=lambda x: x["name"]))

    async def handle_install_components(self, request): return self._json_response({"error": "Not implemented"}, status=501)
    async def handle_delete_components(self, request): return self._json_response({"error": "Not implemented"}, status=501)
    async def handle_patch_component_state(self, request):
        resource_type = request.match_info.get("resource_type") or request.path.split("/")[3]
        item_id = request.match_info.get("item_id")
        body = await request.json()
        is_paused = body.get("paused", False)
        manager, error = self._get_manager_for_type(resource_type)
        if error: return self._json_response({"error": error}, status=503)
        prefix = "app" if "widget" in resource_type else resource_type.rstrip('s')
        pause_method = getattr(manager, f"set_{prefix}_paused", None)
        if pause_method and pause_method(item_id, is_paused): return self._json_response({"status": "success"})
        return self._json_response({"error": "Failed"}, status=500)
