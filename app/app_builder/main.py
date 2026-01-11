########################################################################
# WEBSITE https://flowork.cloud
# File NAME : C:\FLOWORK\apps\app_builder\main.py
########################################################################

def run(app_context, action=None, data=None, *args, **kwargs):
    """
    Entry point utama App-Builder.
    Meneruskan perintah ke backend router jika ada action.
    """
    if action:
        # Panggil router yang ada di folder backend
        return app_context.execute_backend("app_router", action=action, data=data)

    return {"status": "ready", "message": "App Builder UI is active."}