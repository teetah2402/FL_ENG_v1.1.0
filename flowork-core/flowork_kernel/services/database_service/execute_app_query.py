########################################################################
# WEBSITE https://flowork.cloud
# File NAME : C:\FLOWORK\flowork-core\flowork_kernel\services\database_service\execute_app_query.py
########################################################################

import logging

def run(hub, app_id: str, query_type: str, collection: str, payload: dict):
    """
    [FIXED] Membolehkan App membaca variabel GLOBAL tanpa hambatan owner_app_id.
    """
    hub.logger.info(f"🏦 [IronBank] Filtering request from {app_id} for {collection}")

    try:
        # 1. SECURITY CHECK
        system_tables = ["users", "system_logs", "engine_vitals", "provided_services"]

        if collection.lower() in system_tables:
            if query_type.lower() in ["delete", "update", "insert"]:
                raise PermissionError(f"Akses Ditolak! App {app_id} dilarang modifikasi tabel sistem.")

        # 2. NAMESPACE SCOPING (Isolasi Data)
        # Jika App akses 'app_storage', dia cuma boleh liat miliknya sendiri
        if collection == "app_storage":
            payload["owner_app_id"] = app_id
            hub.logger.info(f"🔒 [IronBank] Scoping storage to: {app_id}")

        # [FIX] Jika App akses 'variables', jangan di-scope! Variabel bersifat GLOBAL.
        elif collection == "variables":
            hub.logger.info(f"🔓 [IronBank] Global Variable access granted for {app_id}")

        # 3. EKSEKUSI
        return hub.transaction(query_type, collection, payload)

    except Exception as e:
        hub.logger.error(f"❌ [IronBank-Error] {str(e)}")
        return {"status": "error", "message": f"Iron Bank Access Denied: {str(e)}"}