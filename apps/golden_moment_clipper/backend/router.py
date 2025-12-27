########################################################################
# WEBSITE https://flowork.cloud
# File NAME : C:\flowork-nano\apps\golden_moment_clipper\backend\router.py total lines 53 
########################################################################

import asyncio
import threading
from aiohttp import web

class AppRouter:
    def __init__(self, service):
        self.service = service

    def get_routes(self):
        return {
            "start_processing": self.start_processing,
            "progress": self.progress_check,
            "browse_directory": self.browse_handler,
            "status": self.status_handler
        }

    async def browse_handler(self, payload: dict):
        path = payload.get("path")
        user_id = payload.get("user_context", {}).get("user_id", "system")

        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, self.service.list_directory, path, user_id)
        return result

    async def start_processing(self, payload: dict):
        user_id = payload.get("user_context", {}).get("user_id", "system")

        if not payload.get("input_folder_path") or not payload.get("output_folder"):
            return {"status": "error", "error": "Missing input/output folder"}

        job_id = self.service.init_job(user_id)

        t = threading.Thread(
            target=self.service.run_process_safe,
            args=(job_id, payload, user_id),
            daemon=True
        )
        t.start()

        return {"status": "success", "job_id": job_id}

    async def progress_check(self, payload: dict):
        job_id = payload.get("job_id")
        return self.service.get_job_status(job_id)

    async def status_handler(self, payload: dict):
        return {"status": "online", "service": "Golden Moment Studio"}
