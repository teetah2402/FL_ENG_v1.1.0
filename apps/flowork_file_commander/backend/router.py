########################################################################
# WEBSITE https://flowork.cloud
# File NAME : C:\flowork-nano\apps\flowork_file_commander\backend\router.py total lines 78 
########################################################################

import asyncio
from aiohttp import web

class AppRouter:
    def __init__(self, service):
        self.service = service

    def get_routes(self):
        return {
            "browse": self.browse_handler,
            "create": self.create_handler,
            "delete": self.delete_handler,
            "delete_batch": self.delete_batch_handler, # NEW
            "rename": self.rename_handler,             # NEW
            "read": self.read_handler,
            "download_file": self.download_handler,
            "status": self.status_handler
        }

    async def browse_handler(self, payload: dict):
        path = payload.get("path")
        user_id = payload.get("user_context", {}).get("user_id", "system")
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.service.list_files, path, user_id)

    async def create_handler(self, payload: dict):
        path = payload.get("path")
        name = payload.get("name")
        user_id = payload.get("user_context", {}).get("user_id", "system")
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.service.create_new_folder, path, name, user_id)

    async def delete_handler(self, payload: dict):
        path = payload.get("path")
        user_id = payload.get("user_context", {}).get("user_id", "system")
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.service.delete_item, path, user_id)

    async def delete_batch_handler(self, payload: dict):
        paths = payload.get("paths", [])
        user_id = payload.get("user_context", {}).get("user_id", "system")
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.service.delete_batch_items, paths, user_id)

    async def rename_handler(self, payload: dict):
        path = payload.get("path")
        new_name = payload.get("new_name")
        user_id = payload.get("user_context", {}).get("user_id", "system")

        if not new_name: return {"status": "error", "error": "New name required"}

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.service.rename_item, path, new_name, user_id)

    async def read_handler(self, payload: dict):
        path = payload.get("path")
        user_id = payload.get("user_context", {}).get("user_id", "system")
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.service.read_file_content, path, user_id)

    async def download_handler(self, payload: dict):
        path = payload.get("path")
        user_id = payload.get("user_context", {}).get("user_id", "system")
        real_path = self.service.get_download_path(path, user_id)

        if real_path:
            return web.FileResponse(real_path)
        else:
            return web.json_response({"error": "File not found"}, status=404)

    async def status_handler(self, payload: dict):
        return {"status": "online", "service_id": self.service.service_id}
