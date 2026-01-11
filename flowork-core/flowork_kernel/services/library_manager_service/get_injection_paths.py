########################################################################
# WEBSITE https://flowork.cloud
# File NAME : C:\FLOWORK\flowork-core\flowork_kernel\services\library_manager_service\get_injection_paths.py total lines 45
########################################################################

import os
import sys
import hashlib

def run(hub, app_id: str):
    """
    [PHASE 1 - MASTER SYNC]
    Disederhanakan untuk mensupport semua struktur Warehouse (Root & Hashed).
    """
    injection_paths = []

    # 1. Path Internal App
    app_backend = os.path.abspath(os.path.join(hub.kernel.apps_path, app_id, "backend"))
    if os.path.exists(app_backend): injection_paths.append(app_backend)

    # 2. Warehouse Discovery
    warehouse_base = getattr(hub, 'warehouse_path', os.path.join(hub.kernel.data_path, "global_libs"))

    if os.path.exists(warehouse_base):
        for entry in os.scandir(warehouse_base):
            if entry.is_dir():
                # Masukkan root lib (AI Council Style)
                injection_paths.append(entry.path)
                # Masukkan semua sub-hash (LibraryManager Style)
                for sub in os.scandir(entry.path):
                    if sub.is_dir(): injection_paths.append(sub.path)

    hub.logger.debug(f"💉 [Logistics] Injected {len(injection_paths)} paths for {app_id}")
    return list(set(injection_paths))