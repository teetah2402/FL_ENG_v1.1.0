########################################################################
# WEBSITE https://flowork.cloud
# File NAME : C:\flowork-nano\flowork-core\flowork_kernel\services\base_service.py total lines 157 
########################################################################

import logging
import os
import shutil
import time
from pathlib import Path
from flowork_kernel.utils.path_helper import get_data_directory, resolve_user_path

class BaseService:
    def __init__(self, kernel, service_id: str):
        self.kernel = kernel
        self.service_id = service_id
        self.name = service_id
        self.logger = logging.getLogger(f"flowork.{service_id}")
        self._progress_trackers = {}

    async def start(self):
        pass

    async def stop(self):
        pass

    def register_routes(self, router_bridge):
        pass

    def broadcast_progress(self, percent: str, message: str, job_id: str = "global", throttle_sec: float = 1.0, force: bool = False):
        now = time.time()
        last_time = self._progress_trackers.get(job_id, 0)

        if force or (now - last_time >= throttle_sec):
            log_msg = f"⏳ [{job_id}] {percent} | {message}"
            if "100%" in percent or percent == "DONE":
                log_msg = f"✅ [{job_id}] COMPLETED | {message}"

            self.kernel.write_to_log(log_msg, "INFO")
            self._progress_trackers[job_id] = now


    def _get_user_jail(self, user_id: str) -> Path:
        """
        [FIX] STRICT JAIL:
        Tidak ada pengecualian. 'system' pun harus masuk ke /data/users/system.
        Tidak boleh ada yang akses langsung ke /data/.
        """
        safe_id = str(user_id).strip()

        if not safe_id or safe_id in ["None", "null", "undefined"]:
            safe_id = "system"

        base_data = get_data_directory()
        jail_path = base_data / "users" / safe_id

        if not jail_path.exists():
            jail_path.mkdir(parents=True, exist_ok=True)

        return jail_path.resolve()

    def _is_safe_path(self, target_path: Path, jail_root: Path) -> bool:
        """Polisi Path: Memastikan tidak ada yang kabur dari penjara"""
        try:
            abs_target = target_path.resolve()
            abs_jail = jail_root.resolve()
            return str(abs_target).startswith(str(abs_jail))
        except:
            return False

    def _resolve_and_secure_path(self, raw_path: str, user_id: str):
        """Helper sakti untuk menormalisasi path dan memastikan keamanan"""
        user_jail = self._get_user_jail(user_id)

        if not raw_path or raw_path in ["undefined", "null", "root", "default", "C:/", "/"]:
            return user_jail, user_jail

        target_path = Path(raw_path)

        if os.name != 'nt' and ':' in str(target_path):
            clean = str(target_path).split(':')[-1].replace('\\', '/').strip('/')
            target_path = Path('/') / clean

        try:
            final_path = target_path.resolve()
        except:
            final_path = (user_jail / raw_path).resolve()

        if not self._is_safe_path(final_path, user_jail):
            self.logger.warning(f"[Security] Blocked access to {final_path} for user {user_id}. Redirecting to jail.")
            return user_jail, user_jail

        return final_path, user_jail


    def secure_list_directory(self, path: str, user_id: str):
        try:
            target_path, user_jail = self._resolve_and_secure_path(path, user_id)

            if not target_path.exists():
                try: target_path.mkdir(parents=True, exist_ok=True)
                except: target_path = user_jail

            items = []

            if str(target_path) != str(user_jail):
                 items.append({"name": "..", "type": "directory", "path": str(target_path.parent), "icon": "mdi-folder-upload"})

            for entry in os.scandir(target_path):
                try:
                    kind = "directory" if entry.is_dir() else "file"
                    icon = "mdi-folder" if entry.is_dir() else "mdi-file"
                    items.append({"name": entry.name, "type": kind, "path": entry.path, "icon": icon})
                except: continue

            items.sort(key=lambda x: (x["type"] != "directory", x["name"].lower()))
            return {"current_path": str(target_path), "items": items}

        except Exception as e:
            self.logger.error(f"[SecureFS] List Error: {e}")
            return {"error": str(e), "items": []}

    def secure_create_folder(self, current_path: str, folder_name: str, user_id: str):
        try:
            base_path, user_jail = self._resolve_and_secure_path(current_path, user_id)
            target_path = base_path / folder_name

            if not self._is_safe_path(target_path, user_jail):
                return {"error": "Access Denied"}

            if target_path.exists():
                return {"error": "Folder already exists"}

            target_path.mkdir(parents=True, exist_ok=True)
            return {"status": "success", "path": str(target_path)}
        except Exception as e:
            return {"error": str(e)}

    def secure_delete_path(self, path: str, user_id: str):
        try:
            target_path, user_jail = self._resolve_and_secure_path(path, user_id)

            if target_path == user_jail:
                return {"error": "Cannot delete root folder"}

            if not target_path.exists():
                return {"error": "Path not found"}

            if target_path.is_dir():
                shutil.rmtree(target_path)
            else:
                os.remove(target_path)

            return {"status": "success"}
        except Exception as e:
            return {"error": str(e)}
