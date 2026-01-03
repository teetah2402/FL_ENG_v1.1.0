########################################################################
# WEBSITE https://flowork.cloud
# File NAME : C:\FLOWORK\app\universal_downloader\backend\app_router.py total lines 171 
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

        self.logger = logging.getLogger("AppRouter.UniversalDownloader")

        try:
            service_file = os.path.join(backend_path, "app_service.py")
            spec = importlib.util.spec_from_file_location("ud_isolated_service", service_file)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            self.service = mod.UniversalDownloaderService(real_kernel, "flowork_universal_downloader")
            self.logger.info("🔗 [AppRouter] Neural Downloader Service Locked & Loaded.")
        except Exception as e:
            self.logger.error(f"🔥 Isolated Import Failed: {e}")
            self.service = getattr(app_context, 'service', None)

        self.logger.info("🔗 [AppRouter] Router ONLINE. Siap meneruskan perintah ke Service.")

    def get_routes(self):
        """[English Note] Explicit route mapping for GUI index.html actions."""
        return {
            "browse": self.browse_handler,
            "browse_directory": self.browse_handler,
            "read": self.read_handler,

            "create": self.create_handler,
            "create_folder": self.create_handler,
            "create_new_folder": self.create_handler,

            "delete": self.delete_handler,
            "delete_item": self.delete_handler,
            "delete_batch": self.delete_batch_handler,

            "rename": self.rename_handler,

            "download_file": self.download_handler,
            "start_download": self.start_download_handler,
            "quick_download": self.start_download_handler, # Alias to background start

            "check_job": self.check_job_handler,
            "status": self.status_handler,

            "progress": self.progress_handler
        }

    def _get_user_id(self, payload):
        uid = payload.get("user_id")
        if not uid:
            uid = payload.get("user_context", {}).get("user_id")
        if not uid:
            uid = "system"
        return uid

    async def browse_handler(self, payload: dict):
        path = payload.get("path") or payload.get("current_path")
        user_id = self._get_user_id(payload)


        return await self.service.list_files(path, user_id)

    async def create_handler(self, payload: dict):
        path = payload.get("path") or payload.get("current_path")
        name = payload.get("name") or payload.get("folder_name")
        user_id = self._get_user_id(payload)
        if not name: return {"status": "error", "error": "Folder name missing"}


        return await self.service.create_new_folder(path, name, user_id)

    async def delete_handler(self, payload: dict):
        path = payload.get("path") or payload.get("target_path")
        user_id = self._get_user_id(payload)
        if not path: return {"status": "error", "error": "Path missing"}


        return await self.service.delete_item(path, user_id)

    async def delete_batch_handler(self, payload: dict):
        paths = payload.get("paths", [])
        user_id = self._get_user_id(payload)


        return await self.service.delete_batch_items(paths, user_id)

    async def rename_handler(self, payload: dict):
        path = payload.get("path") or payload.get("target_path")
        new_name = payload.get("new_name")
        user_id = self._get_user_id(payload)
        if not new_name: return {"status": "error", "error": "New name required"}


        return await self.service.rename_item(path, new_name, user_id)

    async def read_handler(self, payload: dict):
        path = payload.get("path")
        user_id = self._get_user_id(payload)


        return await self.service.read_file_content(path, user_id)

    async def download_handler(self, payload: dict):
        """Handle file download (serving the file back to client)"""
        path = payload.get("path")
        user_id = self._get_user_id(payload)
        if hasattr(self.service, 'get_download_path'):
             real_path = self.service.get_download_path(path, user_id)
             if real_path and os.path.exists(real_path):
                 return web.FileResponse(real_path)

        return web.json_response({"error": "File not found or access denied"}, status=404)

    async def start_download_handler(self, payload: dict):
        """
        [MODIFIED] Now uses Background Job Starter with Proper User ID.
        This enables Muscle delegation if configured in Service.
        """
        user_id = self._get_user_id(payload)

        url = payload.get('url')
        format_mode = payload.get('format_mode', 'best')
        output_folder = payload.get('output_folder') or payload.get('output_dir')

        self.logger.info(f"📥 [Router] Download Request received for: {url} (User: {user_id})")

        return await self.service.start_background_download(url, output_folder, format_mode, user_id)

    async def check_job_handler(self, payload: dict):
        job_id = payload.get("job_id")
        return await self.service.get_job_status(job_id)

    async def progress_handler(self, payload: dict):
        job_id = payload.get("job_id")
        if hasattr(self.service, 'get_job_progress'):
            return await self.service.get_job_progress(job_id)
        return {"status": "error", "message": "Progress engine not supported by service"}

    async def status_handler(self, payload: dict):
        has_muscle = False
        if hasattr(self.service, 'muscle') and self.service.muscle:
            has_muscle = True

        return {
            "status": "online",
            "app": "universal_downloader",
            "backend": "hybrid_router_v2_async",
            "muscle_mode": has_muscle
        }
