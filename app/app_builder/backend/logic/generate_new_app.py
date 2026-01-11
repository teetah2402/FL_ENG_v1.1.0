########################################################################
# WEBSITE https://flowork.cloud
# File NAME : C:\FLOWORK\apps\app_builder\backend\logic\generate_new_app.py
########################################################################
import os
import json

def run(context, data, *args, **kwargs):
    """
    Evolutionary Hands: Menulis aplikasi custom secara fisik tanpa template kaku.
    """
    app_id = data.get('app_id', '').strip()
    bundle = data.get('bundle', {}) # Mendapat bundle dari AI Architect

    if not app_id:
        return {"status": "error", "message": "App ID wajib ada untuk identitas saraf."}

    try:
        kernel = getattr(context, 'kernel', None)
        app_service = kernel.get_service('app_service')

        # 1. Inisialisasi Ruang Saraf (Folder App)
        res = app_service.scaffold_app(app_id)
        if res.get('status') != 'success': return res

        app_dir = os.path.join(app_service.base_app_path, app_id)
        backend_dir = os.path.join(app_dir, "backend")
        logic_dir = os.path.join(backend_dir, "logic")
        os.makedirs(logic_dir, exist_ok=True)

        # 2. THE HANDS: Menulis file sesuai visi AI
        # Jika bundle ada, gunakan konten dari AI. Jika tidak, gunakan default.
        files_to_deploy = {
            os.path.join(app_dir, "index.html"): bundle.get('index_html'),
            os.path.join(app_dir, "manifest.json"): json.dumps(bundle.get('manifest', {}), indent=4) if bundle.get('manifest') else None,
            os.path.join(app_dir, "main.py"): bundle.get('main_py'),
            os.path.join(app_dir, "icon.svg"): bundle.get('icon_svg'),
            os.path.join(backend_dir, "app_router.py"): bundle.get('app_router_py'),
            os.path.join(backend_dir, "app_service.py"): bundle.get('app_service_py'),
            os.path.join(logic_dir, "main_logic.py"): bundle.get('main_logic_py')
        }

        for path, content in files_to_deploy.items():
            if content:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(content)

        # 3. Fallback Logic (Jika AI hanya kirim kode deskripsi)
        if not bundle and data.get('description'):
            desc = data.get('description')
            with open(os.path.join(logic_dir, "main_logic.py"), 'w', encoding='utf-8') as f:
                if "def run" not in desc:
                    desc = f"def run(app_context, data, *args, **kwargs):\n    " + "\n    ".join(desc.split('\n'))
                f.write(desc)

        app_service.sync()
        return {
            "status": "success",
            "message": f"EVOLUTION_COMPLETE: '{app_id}' telah lahir secara otonom."
        }

    except Exception as e:
        return {"status": "error", "message": f"HANDS_FAULT: {str(e)}"}