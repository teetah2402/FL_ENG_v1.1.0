########################################################################
# WEBSITE https://flowork.cloud
# File NAME : C:\flowork-nano\apps\universal_downloader\backend\router.py total lines 81 
########################################################################

import asyncio
import os
import threading
from aiohttp import web

class AppRouter:
    def __init__(self, service):
        self.service = service

    def get_routes(self):
        return {
            "download": self.download_handler,
            "quick_download": self.download_handler,
            "browse_directory": self.browse_handler,
            "create_folder": self.create_folder_handler,
            "delete_item": self.delete_item_handler,
            "progress": self.progress_handler,
            "status": self.status_handler
        }

    async def progress_handler(self, payload: dict):
        job_id = payload.get("job_id")
        status = self.service.get_job_progress(job_id)
        return status

    async def create_folder_handler(self, payload: dict):
        path = payload.get("current_path")
        name = payload.get("folder_name")
        user_id = payload.get("user_context", {}).get("user_id", "system")

        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, self.service.create_folder, path, name, user_id)
        return result

    async def delete_item_handler(self, payload: dict):
        path = payload.get("target_path")
        user_id = payload.get("user_context", {}).get("user_id", "system")

        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, self.service.delete_path, path, user_id)
        return result

    async def browse_handler(self, payload: dict):
        path = payload.get("path")
        user_id = payload.get("user_context", {}).get("user_id", "system")

        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, self.service.list_directory, path, user_id)
        return result

    async def download_handler(self, payload: dict):
        url = payload.get("url")
        user_id = payload.get("user_context", {}).get("user_id", "system")

        options = {
            "format": payload.get("format_mode", "best"),
            "proxy_url": payload.get("proxy_url"),
            "cookie_file": payload.get("cookie_file"),
            "output_folder": payload.get("output_folder")
        }

        if not url: return {"error": "URL is required"}

        job_id = self.service.start_download_task(url, user_id, options)
        t = threading.Thread(
            target=self.service.execute_download,
            args=(job_id, url, user_id, options),
            daemon=True
        )
        t.start()

        return {"status": "processing_started", "message": "Job initiated.", "job_id": job_id}

    async def status_handler(self, payload: dict):
        return {"status": "online", "service_id": self.service.service_id}
