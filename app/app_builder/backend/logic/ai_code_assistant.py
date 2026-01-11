########################################################################
# WEBSITE https://flowork.cloud
# File NAME : C:\FLOWORK\apps\app_builder\backend\logic\ai_code_assistant.py
########################################################################
import os
import json
import re
import logging

def scrub_and_parse(text):
    """Mengekstrak JSON secara brutal dan melakukan normalisasi kunci."""
    # 1. Bersihkan Markdown
    clean = re.sub(r'```json|```py|```python|```', '', text).strip()

    # 2. Ambil blok kurung kurawal
    match = re.search(r'(\{.*\})', clean, re.DOTALL)
    if not match: return None

    try:
        data = json.loads(match.group(1))
        # 3. NORMALISASI KUNCI (Mencegah Undefined)
        return {
            "manifest": data.get("manifest", {}),
            "index_html": data.get("index_html") or data.get("html") or "",
            "main_py": data.get("main_py") or data.get("main") or "",
            "app_router_py": data.get("app_router_py") or data.get("router") or "",
            "app_service_py": data.get("app_service_py") or data.get("service") or "",
            "main_logic_py": data.get("main_logic_py") or data.get("logic") or data.get("main_logic") or "",
            "icon_svg": data.get("icon_svg") or data.get("icon") or "<svg></svg>"
        }
    except:
        return None

def run(context, data, *args, **kwargs):
    prompt = data.get('prompt', '').strip()
    target_model = data.get('model')
    user_id = data.get('user_id') or getattr(context, 'user_id', None) or kwargs.get('user_id')

    try:
        kernel = getattr(context, 'kernel', None)
        ai_service = kernel.get_service('ai_provider_manager_service')

        # Load Blueprint
        app_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        ref_path = os.path.join(app_root, "templates", "contohapp.TXT")
        ref_content = open(ref_path, 'r').read()[:20000] if os.path.exists(ref_path) else ""

        instruction = (
            "TASK: GENERATE COMPLETE APP BUNDLE.\n"
            "FORMAT: JSON ONLY. NO TEXT.\n"
            "STRUCTURE: {\"manifest\":{}, \"index_html\":\"\", \"main_logic_py\":\"\", \"icon_svg\":\"\"}\n"
            f"REFERENCE ARS:\n{ref_content}\n"
            f"PROMPT: {prompt}"
        )

        response = ai_service.run({"action": "generate", "prompt": instruction, "user_id": user_id, "model": target_model})

        raw_res = ""
        if isinstance(response, dict):
            if response.get('status') == 'error': return response
            raw_res = response.get('data') or response.get('response') or ""
        else: raw_res = str(response)

        # Proses dengan Saraf Normalizer
        bundle = scrub_and_parse(raw_res)

        if bundle:
            # Suntikkan skeleton standar jika AI lupa
            if not bundle["main_py"]: bundle["main_py"] = "def run(c, a=None, d=None, *args, **kwargs):\n    if a: return c.execute_backend('app_router', action=a, data=d)\n    return {'status': 'ready'}"
            if not bundle["app_router_py"]: bundle["app_router_py"] = "def route(c, a, d=None): return c.execute_logic('backend.logic.main_logic', d)"

            return {"status": "success", "app_bundle": bundle}

        # Fallback jika gagal JSON
        return {"status": "success", "code_suggestion": raw_res}

    except Exception as e:
        return {"status": "error", "message": f"SYSTEM_FAULT: {str(e)}"}