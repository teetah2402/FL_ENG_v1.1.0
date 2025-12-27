########################################################################
# WEBSITE https://flowork.cloud
# File NAME : C:\flowork-nano\flowork-core\flowork_kernel\utils\path_helper.py total lines 59 
########################################################################

import os
import sys
from pathlib import Path

IS_DOCKER = os.path.exists("/.dockerenv") or os.environ.get("FLOWORK_ENV") == "production"

def get_apps_directory():
    """
    Mengembalikan path absolut ke folder apps yang benar.
    """
    if IS_DOCKER:
        return Path("/app/flowork_kernel/apps")
    else:
        dev_path = Path("C:/FLOWORK/apps")
        if dev_path.exists():
            return dev_path

        local_fallback = Path(os.getcwd()) / "apps"
        local_fallback.mkdir(exist_ok=True)
        return local_fallback

def get_data_directory():
    """
    Mengembalikan path ke folder data global (tempat DB, user uploads, dll).
    Ditambahkan untuk memperbaiki error impor di Universal Downloader.
    """
    if IS_DOCKER:
        data_path = Path("/app/data")
    else:
        dev_data_path = Path("C:/FLOWORK/data")
        if dev_data_path.parent.exists(): # Cek C:/FLOWORK ada gak
             if not dev_data_path.exists():
                 dev_data_path.mkdir(exist_ok=True)
             data_path = dev_data_path
        else:
             data_path = Path(os.getcwd()) / "data"

    data_path.mkdir(parents=True, exist_ok=True)
    return data_path

def resolve_user_path(user_id: str) -> Path:
    """
    Mengembalikan path khusus user untuk nyimpen file privat.
    Struktur: {DATA_DIR}/users/{user_id}
    """
    data_dir = get_data_directory()
    user_path = data_dir / "users" / user_id
    user_path.mkdir(parents=True, exist_ok=True)
    return user_path

def normalize_path(path_str):
    """Benerin slash biar gak error di Windows/Linux"""
    return str(Path(path_str).resolve())
