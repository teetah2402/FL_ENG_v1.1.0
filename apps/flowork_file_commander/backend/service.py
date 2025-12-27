########################################################################
# WEBSITE https://flowork.cloud
# File NAME : C:\flowork-nano\apps\flowork_file_commander\backend\service.py total lines 110 
########################################################################

import os
import shutil
from pathlib import Path
from flowork_kernel.services.base_service import BaseService

class FileManagerService(BaseService):
    def __init__(self, kernel, service_id: str):
        super().__init__(kernel, service_id)
        self.name = "Flowork File Manager"
        self.kernel.write_to_log(f"[{self.name}] Service Initialized.", "INFO")

    def start(self):
        self.kernel.write_to_log(f"[{self.name}] Ready.", "SUCCESS")

    def stop(self):
        pass

    def list_files(self, path: str, user_id: str):
        return self.secure_list_directory(path, user_id)

    def create_new_folder(self, current_path: str, name: str, user_id: str):
        return self.secure_create_folder(current_path, name, user_id)

    def delete_item(self, path: str, user_id: str):
        return self.secure_delete_path(path, user_id)


    def rename_item(self, path: str, new_name: str, user_id: str):
        """
        Rename file atau folder.
        Menggunakan _resolve_and_secure_path dari BaseService untuk keamanan.
        """
        try:
            target_path, jail_root = self._resolve_and_secure_path(path, user_id)

            if not target_path.exists():
                return {"status": "error", "error": "Item not found"}

            new_path = target_path.parent / new_name

            try:
                new_path.relative_to(jail_root)
            except ValueError:
                return {"status": "error", "error": "Access Denied: Path escape attempt"}

            if new_path.exists():
                return {"status": "error", "error": "Name already exists"}

            target_path.rename(new_path)

            self.kernel.write_to_log(f"[{self.name}] Renamed: {target_path.name} -> {new_name}", "INFO")
            return {"status": "success"}

        except Exception as e:
            self.kernel.write_to_log(f"[{self.name}] Rename Error: {str(e)}", "ERROR")
            return {"status": "error", "error": str(e)}

    def delete_batch_items(self, paths: list, user_id: str):
        """
        Menghapus banyak item sekaligus.
        """
        deleted_count = 0
        errors = []

        for path in paths:
            result = self.secure_delete_path(path, user_id)

            if result.get("status") == "success":
                deleted_count += 1
            else:
                errors.append(f"{os.path.basename(path)}: {result.get('error')}")

        if deleted_count > 0:
            self.kernel.write_to_log(f"[{self.name}] Batch Delete: {deleted_count} items removed.", "INFO")

        return {
            "status": "success" if deleted_count > 0 else "error",
            "deleted": deleted_count,
            "errors": errors
        }

    def read_file_content(self, path: str, user_id: str):
        try:
            target_path, _ = self._resolve_and_secure_path(path, user_id)
            if not target_path.exists() or not target_path.is_file():
                return {"error": "Invalid file"}

            if target_path.stat().st_size > 1024 * 1024:
                return {"error": "File too large for preview"}

            with open(target_path, 'r', encoding='utf-8') as f:
                return {"status": "success", "content": f.read()}
        except UnicodeDecodeError:
            return {"error": "Binary file"}
        except Exception as e:
            return {"error": str(e)}

    def get_download_path(self, path: str, user_id: str):
        try:
            target_path, _ = self._resolve_and_secure_path(path, user_id)
            if target_path.exists() and target_path.is_file():
                return str(target_path)
            return None
        except: return None
