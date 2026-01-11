########################################################################
# WEBSITE https://flowork.cloud
# File NAME : C:\FLOWORK\apps\app_builder\backend\logic\get_app_logs.py
########################################################################
import os

def run(context, data, *args, **kwargs):
    """
    The Eyes: Membaca log untuk feedback loop evolusi.
    """
    app_id = data.get('app_id')
    # Path log universal Flowork
    log_path = "C:\\FLOWORK\\logs\\flowork.log" if os.name == 'nt' else "/app/logs/flowork.log"

    if not os.path.exists(log_path):
        return {"status": "error", "message": "Log file not discovered."}

    try:
        with open(log_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            # Ambil 100 baris terakhir yang relevan dengan App ID
            relevant = [l for l in lines if app_id in l][-100:]
            return {"status": "success", "logs": "".join(relevant)}
    except Exception as e:
        return {"status": "error", "message": str(e)}