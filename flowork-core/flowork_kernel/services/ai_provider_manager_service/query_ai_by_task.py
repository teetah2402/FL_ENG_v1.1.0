########################################################################
# WEBSITE [https://flowork.cloud](https://flowork.cloud)
# File NAME : C:\FLOWORK\flowork-core\flowork_kernel\services\ai_provider_manager_service\query_ai_by_task.py
########################################################################

import os
import json
import logging

def run(hub, task_type: str, prompt: str, endpoint_id: str=None, messages: list=None, stream: bool=False, **kwargs):
    """
    Logic routing AI dengan Automatic Secret Injection (Tiru AI Council/Chat App).
    """
    target = endpoint_id
    user_id = kwargs.get('user_id')

    # --- [SECRET INJECTOR] TIRU AI COUNCIL ---
    # Memastikan API Key disuntikkan ke environment sebelum provider dipanggil
    try:
        var_service = hub.kernel.get_service('variable_manager')
        if var_service:
            # Daftar key yang harus disinkronkan dari Neural Vault ke OS Environ
            keys_to_sync = ["OPENAI_API_KEY", "GEMINI_API_KEY", "DEEPSEEK_API_KEY"]
            for k in keys_to_sync:
                val = var_service.get_variable(k, user_id=user_id)
                if val:
                    os.environ[k] = str(val)
    except Exception as e:
        hub.logger.error(f"⚠️ [Secret Injector] Fail to sync secrets: {str(e)}")

    # --- [SMART AUTO-SELECT] ---
    if not target:
        if hub.local_models:
            target = list(hub.local_models.keys())[0]
            hub.logger.info(f"💡 [AI AUTO-SELECT] Picking local model: {target}")
        elif hub.loaded_providers:
            for pid, p in hub.loaded_providers.items():
                if hasattr(p, 'list_available_models'):
                    models = p.list_available_models()
                    if models:
                        target = models[0]
                        hub.logger.info(f"💡 [AI AUTO-SELECT] Picking from provider '{pid}': {target}")
                        break

    if not target:
        return {'status': 'error', 'message': 'No AI model found in Neural Matrix.'}

    hub.logger.info(f"[AI Query] Final Target: {target} | User: {user_id}")

    # --- ROUTING EXECUTION ---

    # 1. Direct Provider Match (Jika endpoint_id adalah ID Provider)
    if target in hub.loaded_providers:
        p = hub.loaded_providers[target]
        if hasattr(p, 'generate_response'):
            return p.generate_response(prompt, stream=stream, **kwargs)
        return p.generate(prompt, **kwargs)

    # 2. Model Name Match (Scan semua provider yang terdaftar)
    found_provider = None
    for (pid, p) in hub.loaded_providers.items():
        if hasattr(p, 'list_available_models'):
            try:
                available = p.list_available_models()
                # Case-insensitive match untuk stabilitas neural
                if any(target.lower() == m.lower() for m in available):
                    found_provider = p
                    break
            except:
                continue

    if found_provider:
        kwargs['model'] = target
        if hasattr(found_provider, 'generate_response'):
            return found_provider.generate_response(prompt, stream=stream, **kwargs)
        return found_provider.generate(prompt, **kwargs)

    # 3. Local Model Match
    if target in hub.local_models:
        m = hub.local_models[target]
        if m['type'] == 'gguf':
            return hub.execute_sync('_run_gguf', m, prompt, messages, stream=stream)

    return {'status': 'error', 'message': f'Endpoint {target} not found in Neural Matrix.'}