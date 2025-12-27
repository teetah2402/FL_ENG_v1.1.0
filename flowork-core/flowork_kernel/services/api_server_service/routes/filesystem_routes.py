########################################################################
# WEBSITE https://flowork.cloud
# File NAME : C:\flowork-nano\flowork-core\flowork_kernel\services\api_server_service\routes\filesystem_routes.py total lines 230 
########################################################################

import os
import shutil
import json
import logging
from aiohttp import web
from fastapi import HTTPException # We keep this for consistency with types if needed

logger = logging.getLogger(__name__)


def get_current_user_id(request) -> str:
    """
    Extract User ID from Headers.
    """
    user_id = request.headers.get("X-User-ID")
    if not user_id:
        return "default_user"
    return user_id

def get_user_workspace_path(user_id: str) -> str:
    base_storage = os.getenv("FLOWORK_DATA_DIR", "./data")
    user_path = os.path.join(base_storage, "users", user_id)

    if not os.path.exists(user_path):
        try:
            os.makedirs(user_path, exist_ok=True)
        except Exception as e:
            logger.error(f"Failed to create workspace for user {user_id}: {e}")

    return os.path.abspath(user_path)

def sanitize_and_resolve_path(user_id: str, relative_path: str) -> str:
    root_path = get_user_workspace_path(user_id)
    clean_rel = relative_path.lstrip(r"/\\")
    if not clean_rel:
        clean_rel = "."
    target_path = os.path.abspath(os.path.join(root_path, clean_rel))

    if not target_path.startswith(root_path):
        logger.warning(f"SECURITY ALERT: User {user_id} tried to escape jail! Target: {target_path}")
        raise PermissionError("Access Denied: Path outside workspace")

    return target_path


async def list_files(request):
    try:
        path = request.query.get('path')
        if not path:
             return {"error": "Missing query param 'path'"}

        user_id = get_current_user_id(request)
        try:
            abs_path = sanitize_and_resolve_path(user_id, path)
        except PermissionError as e:
            return {"error": str(e)}

        if not os.path.exists(abs_path):
            return []
        if not os.path.isdir(abs_path):
            return {"error": "Path is not a directory"}

        items = []
        with os.scandir(abs_path) as entries:
            for entry in entries:
                entry_rel_path = os.path.join(path, entry.name).replace("\\", "/")
                items.append({
                    "name": entry.name,
                    "path": entry_rel_path,
                    "type": 'directory' if entry.is_dir() else 'file',
                    "size": entry.stat().st_size if entry.is_file() else 0,
                    "modified": entry.stat().st_mtime
                })
        return items
    except Exception as e:
        logger.error(f"Error listing files: {str(e)}")
        return {"error": str(e)}

async def create_folder(request):
    try:
        try:
            payload = await request.json()
        except:
            return {"error": "Invalid JSON body"}

        path = payload.get("path")
        if not path:
             return {"error": "Missing 'path' in body"}

        user_id = get_current_user_id(request)
        try:
            abs_path = sanitize_and_resolve_path(user_id, path)
        except PermissionError as e:
            return {"error": str(e)}

        if os.path.exists(abs_path):
            return {"status": "error", "message": "Folder already exists"}

        os.makedirs(abs_path, exist_ok=True)
        return {"status": "success", "path": path}
    except Exception as e:
        logger.error(f"Error creating folder: {str(e)}")
        return {"status": "error", "message": str(e)}

async def delete_item(request):
    try:
        path = request.query.get('path')
        if not path:
             return {"error": "Missing query param 'path'"}

        user_id = get_current_user_id(request)
        try:
            abs_path = sanitize_and_resolve_path(user_id, path)
        except PermissionError as e:
            return {"error": str(e)}

        if not os.path.exists(abs_path):
            return {"status": "error", "message": "Item not found"}

        if os.path.isfile(abs_path):
            os.remove(abs_path)
        else:
            shutil.rmtree(abs_path)
        return {"status": "success", "message": f"Deleted {path}"}
    except Exception as e:
        logger.error(f"Error deleting item: {str(e)}")
        return {"status": "error", "message": str(e)}

async def move_item(request):
    try:
        try:
            payload = await request.json()
        except:
            return {"error": "Invalid JSON body"}

        src = payload.get("source")
        dst = payload.get("destination")

        if not src or not dst:
            return {"status": "error", "message": "Missing source or destination"}

        user_id = get_current_user_id(request)
        try:
            src_path = sanitize_and_resolve_path(user_id, src)
            dst_path = sanitize_and_resolve_path(user_id, dst)
        except PermissionError as e:
            return {"error": str(e)}

        if not os.path.exists(src_path):
            return {"status": "error", "message": "Source not found"}
        if os.path.exists(dst_path):
             return {"status": "error", "message": "Destination already exists"}

        shutil.move(src_path, dst_path)
        return {"status": "success", "from": src, "to": dst}
    except Exception as e:
        logger.error(f"Error moving item: {str(e)}")
        return {"status": "error", "message": str(e)}

async def read_file(request):
    try:
        path = request.query.get('path')
        if not path:
             return {"error": "Missing path"}

        user_id = get_current_user_id(request)
        try:
            abs_path = sanitize_and_resolve_path(user_id, path)
        except PermissionError as e:
            return {"error": str(e)}

        if not os.path.exists(abs_path) or not os.path.isfile(abs_path):
            return {"error": "File not found"}

        with open(abs_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return {"content": content}
    except Exception as e:
        logger.error(f"Error reading file: {str(e)}")
        return {"error": str(e)}

async def write_file(request):
    try:
        try:
            payload = await request.json()
        except:
            return {"error": "Invalid JSON body"}

        path = payload.get("path")
        content = payload.get("content")

        if not path or content is None:
            return {"status": "error", "message": "Missing path or content"}

        user_id = get_current_user_id(request)
        try:
            abs_path = sanitize_and_resolve_path(user_id, path)
        except PermissionError as e:
            return {"error": str(e)}

        parent_dir = os.path.dirname(abs_path)
        if not os.path.exists(parent_dir):
            os.makedirs(parent_dir, exist_ok=True)

        with open(abs_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return {"status": "success", "path": path}
    except Exception as e:
        logger.error(f"Error writing file: {str(e)}")
        return {"status": "error", "message": str(e)}

class FilesystemRoutes:
    def __init__(self, service):
        self.service = service

    def register_routes(self):
        return {
            "GET /api/v1/filesystem/list": list_files,
            "POST /api/v1/filesystem/create_folder": create_folder,
            "DELETE /api/v1/filesystem/delete": delete_item,
            "POST /api/v1/filesystem/move": move_item,
            "GET /api/v1/filesystem/read": read_file,
            "POST /api/v1/filesystem/write": write_file
        }
