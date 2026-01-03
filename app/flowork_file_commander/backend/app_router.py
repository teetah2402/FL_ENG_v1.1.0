########################################################################
# WEBSITE https://flowork.cloud
# File NAME : C:\FLOWORK\app\flowork_file_commander\backend\app_router.py total lines 95 
########################################################################

import asyncio
from aiohttp import web
import os
import sys
import importlib.util
import logging

backend_path = os.path.dirname(os.path.abspath(__file__))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

class BaseRouter:
    def __init__(self, kernel):
        self.kernel = kernel


class AppRouter(BaseRouter):
    def __init__(self, app_context):
        real_kernel = getattr(app_context, 'kernel', app_context)
        super().__init__(real_kernel)

        self.logger = logging.getLogger("AppRouter.FileCommander")

        try:
            service_file = os.path.join(backend_path, "app_service.py")
            spec = importlib.util.spec_from_file_location("fc_isolated_service", service_file)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            self.service = mod.FileManagerService(real_kernel, "flowork_file_commander")
            self.logger.info("🔗 [AppRouter] File Commander Service Locked & Loaded.")
        except Exception as e:
            self.logger.error(f"🔥 Isolated Import Failed: {e}")
            self.service = getattr(app_context, 'service', None)

    def get_routes(self):
        """[English Note] Explicit route mapping for GUI index.html actions."""
        return {
            "browse": self.browse_handler,
            "create": self.create_handler,
            "create_folder": self.create_handler,
            "create_file": self.create_file_handler,
            "delete": self.delete_handler,
            "rename": self.rename_handler,
            "read_file": self.read_handler,
            "download_file": self.download_handler,
            "batch_delete": self.batch_delete_handler
        }

    def _get_user_id(self, payload):
        uid = payload.get("user_context", {}).get("user_id")
        if not uid: uid = payload.get("user_id")
        if not uid: uid = "system"
        return uid

    async def browse_handler(self, payload: dict):
        return await self.service.list_files(payload.get("path"), self._get_user_id(payload))

    async def create_handler(self, payload: dict):
        if not payload.get("name"): return {"status": "error", "error": "Folder name required"}
        return await self.service.create_new_folder(payload.get("path"), payload.get("name"), self._get_user_id(payload))

    async def create_file_handler(self, payload: dict):
        if not payload.get("name"): return {"status": "error", "error": "File name required"}
        return await self.service.create_new_file(payload.get("path"), payload.get("name"), payload.get("content", ""), self._get_user_id(payload))

    async def delete_handler(self, payload: dict):
        return await self.service.delete_item(payload.get("path"), self._get_user_id(payload))

    async def batch_delete_handler(self, payload: dict):
        return await self.service.delete_batch_items(payload.get("paths", []), self._get_user_id(payload))

    async def rename_handler(self, payload: dict):
        if not payload.get("new_name"): return {"status": "error", "error": "New name required"}
        return await self.service.rename_item(payload.get("path"), payload.get("new_name"), self._get_user_id(payload))

    async def read_handler(self, payload: dict):
        return await self.service.read_file_content(payload.get("path"), self._get_user_id(payload))

    async def download_handler(self, payload: dict):
        path = payload.get("path")
        user_id = self._get_user_id(payload)
        real_path = await self.service.get_download_path(path, user_id)

        if real_path and os.path.exists(real_path):
            filename = os.path.basename(real_path)
            return web.FileResponse(real_path, headers={
                "Content-Disposition": f"attachment; filename=\"{filename}\""
            })
        return web.Response(text="File not found", status=404)
