from flask import request, current_app
from app.models import RegisteredEngine
from app.helpers import get_db_session
from .utils import _safe_get_session, _resolve_target_engine_sid, _resolve_sid_via_share_token, _inject_fac_if_needed, _broadcast_response, _emit_to_gui

def register_handlers(sio):

    # --- ENGINE RESPONSES (Forward to GUI) ---

    @sio.on('response_component_list', namespace='/engine-socket')
    def on_engine_response_component_list(data):
        sess = _safe_get_session(request.sid, namespace='/engine-socket')
        if not sess: return
        if isinstance(data, dict) and data.get('payload', {}).get('component_type') == 'widgets':
            data['payload']['component_type'] = 'apps'
        engine_id = sess.get('engine_id')
        if engine_id:
            _broadcast_response(engine_id, 'response_component_list', data)
        else:
            _emit_to_gui(sess.get('user_id'), 'response_component_list', data)

    @sio.on('response_variables', namespace='/engine-socket')
    def on_engine_response_variables(data):
        sess = _safe_get_session(request.sid, namespace='/engine-socket')
        if not sess: return
        engine_id = sess.get('engine_id')
        if engine_id:
            _broadcast_response(engine_id, 'response_variables', data)
        else:
            _emit_to_gui(sess.get('user_id'), 'response_variables', data)

    @sio.on('response_presets_list', namespace='/engine-socket')
    def on_engine_response_presets_list(data):
        sess = _safe_get_session(request.sid, namespace='/engine-socket')
        if not sess: return
        engine_id = sess.get('engine_id')
        if engine_id:
            _broadcast_response(engine_id, 'response_presets_list', data)
        else:
            _emit_to_gui(sess.get('user_id'), 'response_presets_list', data)

    @sio.on('response_ai_status', namespace='/engine-socket')
    def on_engine_response_ai_status(data):
        sess = _safe_get_session(request.sid, namespace='/engine-socket')
        if not sess: return
        engine_id = sess.get('engine_id')
        if engine_id:
            _broadcast_response(engine_id, 'response_ai_status', data)
        else:
            _emit_to_gui(sess.get('user_id'), 'response_ai_status', data)

    @sio.on('response_datasets_list', namespace='/engine-socket')
    def on_engine_response_datasets_list(data):
        sess = _safe_get_session(request.sid, namespace='/engine-socket')
        if not sess: return
        engine_id = sess.get('engine_id')
        if engine_id:
            _broadcast_response(engine_id, 'response_datasets_list', data)
        else:
            _emit_to_gui(sess.get('user_id'), 'response_datasets_list', data)

    @sio.on('response_local_models', namespace='/engine-socket')
    def on_engine_response_local_models(data):
        sess = _safe_get_session(request.sid, namespace='/engine-socket')
        if not sess: return
        engine_id = sess.get('engine_id')
        if engine_id:
            _broadcast_response(engine_id, 'response_local_models', data)
        else:
            _emit_to_gui(sess.get('user_id'), 'response_local_models', data)

    @sio.on('response_training_job_status', namespace='/engine-socket')
    def on_engine_response_training_job_status(data):
        sess = _safe_get_session(request.sid, namespace='/engine-socket')
        if not sess: return
        engine_id = sess.get('engine_id')
        if engine_id:
            _broadcast_response(engine_id, 'response_training_job_status', data)
        else:
            _emit_to_gui(sess.get('user_id'), 'response_training_job_status', data)

    @sio.on('component_install_status', namespace='/engine-socket')
    def on_engine_component_install_status(data):
        sess = _safe_get_session(request.sid, namespace='/engine-socket')
        if not sess: return
        if isinstance(data, dict) and data.get('payload', {}).get('component_type') == 'widgets':
            data['payload']['component_type'] = 'apps'
        engine_id = sess.get('engine_id')
        if engine_id:
            _broadcast_response(engine_id, 'component_install_status', data)
        else:
            _emit_to_gui(sess.get('user_id'), 'component_install_status', data)

    @sio.on('response_settings', namespace='/engine-socket')
    @sio.on('settings_state', namespace='/engine-socket')
    def on_engine_response_settings(data):
        sess = _safe_get_session(request.sid, namespace='/engine-socket')
        if not sess: return
        engine_id = sess.get('engine_id')
        user_id = sess.get('user_id')
        if engine_id:
            _broadcast_response(engine_id, 'settings_state', data)
        else:
            _emit_to_gui(user_id, 'settings_state', data)

    @sio.on('FILESYSTEM_LIST_RESPONSE', namespace='/engine-socket')
    def on_engine_filesystem_response(data):
        sess = _safe_get_session(request.sid, namespace='/engine-socket')
        if not sess: return
        user_id = sess.get('user_id')
        _emit_to_gui(user_id, 'FILESYSTEM_LIST_RESPONSE', data)

    @sio.on('response_load_preset', namespace='/engine-socket')
    def on_engine_response_load_preset(data):
        app = current_app._get_current_object()
        sess = _safe_get_session(request.sid, namespace='/engine-socket')
        if not sess: return
        preset_name = "Unknown"
        payload = {}
        if isinstance(data, dict) and data.get('v') == 2:
            payload = data.get('payload') or {}
            preset_name = payload.get('name', 'Unknown')
        target_user_id = payload.get('_target_user_id')
        app.logger.info(f"[Gateway] Received response_load_preset from Engine for preset '{preset_name}'. Forwarding to User {target_user_id or sess.get('user_id')}.")
        engine_id = sess.get('engine_id')
        if engine_id:
            _broadcast_response(engine_id, 'response_load_preset', data)
        else:
            _emit_to_gui(sess.get('user_id'), 'response_load_preset', data)
        if target_user_id and target_user_id != sess.get('user_id'):
             sio.emit('response_load_preset', data, room=str(target_user_id), namespace='/gui-socket')

    # --- GUI REQUESTS (Forward to Engine) ---

    @sio.on('request_presets_list', namespace='/gui-socket')
    def on_request_presets_list(data):
        app = current_app._get_current_object()
        sid = request.sid
        gui_sess = _safe_get_session(sid, namespace='/gui-socket')
        if gui_sess is None: return
        user_id = gui_sess.get('user_id')
        if not isinstance(data, dict) or data.get('v') != 2: return
        payload = data.get('payload', {})
        target_engine_id = payload.get('target_engine_id')
        session = get_db_session()
        try:
            eng_id, eng_sid = _resolve_target_engine_sid(session, user_id, target_engine_id)
            if not eng_id or not eng_sid:
                err_msg = f'Engine {target_engine_id or "active"} is not connected.'
                sio.emit('response_presets_list', {'error': err_msg}, room=sid, namespace='/gui-socket')
                return
            payload['user_context'] = {'id': user_id, 'tier': 'architect'}
            payload = _inject_fac_if_needed(session, user_id, eng_id, payload)
            sio.emit('request_presets_list', {'v': 2, 'payload': payload}, room=eng_sid, namespace='/engine-socket')
        finally:
            session.close()

    @sio.on('request_variables', namespace='/gui-socket')
    def on_request_variables(data):
        app = current_app._get_current_object()
        sid = request.sid
        gui_sess = _safe_get_session(sid, namespace='/gui-socket')
        if gui_sess is None: return
        user_id = gui_sess.get('user_id')
        if not isinstance(data, dict) or data.get('v') != 2: return
        payload = data.get('payload', {})
        target_engine_id = payload.get('target_engine_id')
        session = get_db_session()
        try:
            eng_id, eng_sid = _resolve_target_engine_sid(session, user_id, target_engine_id)
            if not eng_id or not eng_sid:
                sio.emit('response_variables', {'error': 'Engine not connected'}, room=sid, namespace='/gui-socket')
                return
            payload['user_context'] = {'id': user_id, 'tier': 'architect'}
            payload = _inject_fac_if_needed(session, user_id, eng_id, payload)
            sio.emit('request_variables', {'v': 2, 'payload': payload}, room=eng_sid, namespace='/engine-socket')
        finally:
            session.close()

    @sio.on('request_components_list', namespace='/gui-socket')
    def on_request_components_list(data):
        app = current_app._get_current_object()
        sid = request.sid
        gui_sess = _safe_get_session(sid, namespace='/gui-socket')
        if gui_sess is None: return
        user_id = gui_sess.get('user_id')
        if not isinstance(data, dict) or data.get('v') != 2: return
        payload = data.get('payload', {})
        comp_type = payload.get('component_type', 'unknown')
        if comp_type == 'widgets':
            comp_type = 'apps'
            payload['component_type'] = 'apps'
        target_engine_id = payload.get('target_engine_id')
        session = get_db_session()
        try:
            eng_id, eng_sid = _resolve_target_engine_sid(session, user_id, target_engine_id)
            if not eng_id or not eng_sid:
                sio.emit('response_component_list', {'error': 'Engine not connected', 'component_type': comp_type, 'components': []}, room=sid, namespace='/gui-socket')
                return
            payload['user_context'] = {'id': user_id, 'tier': 'architect'}
            payload = _inject_fac_if_needed(session, user_id, eng_id, payload)
            sio.emit('request_components_list', {'v': 2, 'payload': payload}, room=eng_sid, namespace='/engine-socket')
        finally:
            session.close()

    @sio.on('filesystem_list_request', namespace='/gui-socket')
    def on_filesystem_list_request(data):
        app = current_app._get_current_object()
        sid = request.sid
        gui_sess = _safe_get_session(sid, namespace='/gui-socket')
        if gui_sess is None: return
        user_id = gui_sess.get('user_id')
        payload = data if isinstance(data, dict) else {}
        if payload.get('type') == 'filesystem_list_request' and 'path' in payload:
            payload = {'path': payload.get('path'), 'target_engine_id': payload.get('target_engine_id')}
        elif payload.get('v') == 2:
            payload = payload.get('payload', {})
        target_engine_id = payload.get('target_engine_id')
        session = get_db_session()
        try:
            eng_id, eng_sid = _resolve_target_engine_sid(session, user_id, target_engine_id)
            if not eng_id or not eng_sid:
                sio.emit('FILESYSTEM_LIST_RESPONSE', {'error': 'Engine not connected'}, room=sid, namespace='/gui-socket')
                return
            payload['user_context'] = {'id': user_id, 'tier': 'architect'}
            payload = _inject_fac_if_needed(session, user_id, eng_id, payload)
            sio.emit('filesystem_list_request', {'v': 2, 'payload': payload}, room=eng_sid, namespace='/engine-socket')
        finally:
            session.close()

    @sio.on('request_settings', namespace='/gui-socket')
    def on_request_settings(data):
        app = current_app._get_current_object()
        sid = request.sid
        gui_sess = _safe_get_session(sid, namespace='/gui-socket')
        if gui_sess is None: return
        user_id = gui_sess.get('user_id')
        if not isinstance(data, dict) or data.get('v') != 2: return
        payload = data.get('payload', {})
        target_engine_id = payload.get('target_engine_id')
        session = get_db_session()
        try:
            eng_id, eng_sid = _resolve_target_engine_sid(session, user_id, target_engine_id)
            if not eng_id or not eng_sid:
                sio.emit('settings_state', {'error': 'Engine not connected'}, room=sid, namespace='/gui-socket')
                return
            payload['user_context'] = {'id': user_id, 'tier': 'architect'}
            payload = _inject_fac_if_needed(session, user_id, eng_id, payload)
            sio.emit('request_settings', {'v': 2, 'payload': payload}, room=eng_sid, namespace='/engine-socket')
        finally:
            session.close()

    @sio.on('save_settings', namespace='/gui-socket')
    def on_save_settings(data):
        app = current_app._get_current_object()
        sid = request.sid
        gui_sess = _safe_get_session(sid, namespace='/gui-socket')
        if gui_sess is None: return
        user_id = gui_sess.get('user_id')
        if not isinstance(data, dict) or data.get('v') != 2: return
        payload = data.get('payload', {})
        target_engine_id = payload.get('target_engine_id')
        session = get_db_session()
        try:
            eng_id, eng_sid = _resolve_target_engine_sid(session, user_id, target_engine_id)
            if not eng_id or not eng_sid:
                 sio.emit('notification', {'text': 'Save failed: Engine offline', 'color': 'error'}, room=sid, namespace='/gui-socket')
                 return
            payload['user_context'] = {'id': user_id, 'tier': 'architect'}
            payload = _inject_fac_if_needed(session, user_id, eng_id, payload)
            sio.emit('save_settings', {'v': 2, 'payload': payload}, room=eng_sid, namespace='/engine-socket')
        finally:
            session.close()

    @sio.on('update_variable', namespace='/gui-socket')
    def on_update_variable(data):
        sid = request.sid
        gui_sess = _safe_get_session(sid, namespace='/gui-socket')
        if gui_sess is None: return
        user_id = gui_sess.get('user_id')
        if not isinstance(data, dict) or data.get('v') != 2: return
        payload = data.get('payload', {})
        target_engine_id = payload.get('target_engine_id')
        session = get_db_session()
        try:
            eng_id, eng_sid = _resolve_target_engine_sid(session, user_id, target_engine_id)
            if not eng_id or not eng_sid: return
            payload['user_context'] = {'id': user_id, 'tier': 'architect'}
            payload = _inject_fac_if_needed(session, user_id, eng_id, payload)
            sio.emit('update_variable', {'v': 2, 'payload': payload}, room=eng_sid, namespace='/engine-socket')
        finally:
            session.close()

    @sio.on('delete_variable', namespace='/gui-socket')
    def on_delete_variable(data):
        sid = request.sid
        gui_sess = _safe_get_session(sid, namespace='/gui-socket')
        if gui_sess is None: return
        user_id = gui_sess.get('user_id')
        if not isinstance(data, dict) or data.get('v') != 2: return
        payload = data.get('payload', {})
        target_engine_id = payload.get('target_engine_id')
        session = get_db_session()
        try:
            eng_id, eng_sid = _resolve_target_engine_sid(session, user_id, target_engine_id)
            if not eng_id or not eng_sid: return
            payload['user_context'] = {'id': user_id, 'tier': 'architect'}
            payload = _inject_fac_if_needed(session, user_id, eng_id, payload)
            sio.emit('delete_variable', {'v': 2, 'payload': payload}, room=eng_sid, namespace='/engine-socket')
        finally:
            session.close()

    @sio.on('request_prompts_list', namespace='/gui-socket')
    def on_request_prompts_list(data):
        sid = request.sid
        gui_sess = _safe_get_session(sid, namespace='/gui-socket')
        if gui_sess is None: return
        user_id = gui_sess.get('user_id')
        if not isinstance(data, dict) or data.get('v') != 2: return
        payload = data.get('payload', {})
        target_engine_id = payload.get('target_engine_id')
        session = get_db_session()
        try:
            eng_id, eng_sid = _resolve_target_engine_sid(session, user_id, target_engine_id)
            if not eng_id or not eng_sid:
                sio.emit('response_prompts_list', {'error': 'Engine not connected'}, room=sid, namespace='/gui-socket')
                return
            payload['user_context'] = {'id': user_id, 'tier': 'architect'}
            payload = _inject_fac_if_needed(session, user_id, eng_id, payload)
            sio.emit('request_prompts_list', {'v': 2, 'payload': payload}, room=eng_sid, namespace='/engine-socket')
        finally:
            session.close()

    @sio.on('update_prompt', namespace='/gui-socket')
    def on_update_prompt(data):
        sid = request.sid
        gui_sess = _safe_get_session(sid, namespace='/gui-socket')
        if gui_sess is None: return
        user_id = gui_sess.get('user_id')
        if not isinstance(data, dict) or data.get('v') != 2: return
        payload = data.get('payload', {})
        target_engine_id = payload.get('target_engine_id')
        session = get_db_session()
        try:
            eng_id, eng_sid = _resolve_target_engine_sid(session, user_id, target_engine_id)
            if not eng_id or not eng_sid: return
            payload['user_context'] = {'id': user_id, 'tier': 'architect'}
            payload = _inject_fac_if_needed(session, user_id, eng_id, payload)
            sio.emit('update_prompt', {'v': 2, 'payload': payload}, room=eng_sid, namespace='/engine-socket')
        finally:
            session.close()

    @sio.on('delete_prompt', namespace='/gui-socket')
    def on_delete_prompt(data):
        sid = request.sid
        gui_sess = _safe_get_session(sid, namespace='/gui-socket')
        if gui_sess is None: return
        user_id = gui_sess.get('user_id')
        if not isinstance(data, dict) or data.get('v') != 2: return
        payload = data.get('payload', {})
        target_engine_id = payload.get('target_engine_id')
        session = get_db_session()
        try:
            eng_id, eng_sid = _resolve_target_engine_sid(session, user_id, target_engine_id)
            if not eng_id or not eng_sid: return
            payload['user_context'] = {'id': user_id, 'tier': 'architect'}
            payload = _inject_fac_if_needed(session, user_id, eng_id, payload)
            sio.emit('delete_prompt', {'v': 2, 'payload': payload}, room=eng_sid, namespace='/engine-socket')
        finally:
            session.close()

    @sio.on('request_ai_status', namespace='/gui-socket')
    def on_request_ai_status(data):
        sid = request.sid
        gui_sess = _safe_get_session(sid, namespace='/gui-socket')
        if gui_sess is None: return
        user_id = gui_sess.get('user_id')
        if not isinstance(data, dict) or data.get('v') != 2: return
        payload = data.get('payload', {})
        target_engine_id = payload.get('target_engine_id')
        session = get_db_session()
        try:
            eng_id, eng_sid = _resolve_target_engine_sid(session, user_id, target_engine_id)
            if not eng_id or not eng_sid:
                sio.emit('response_ai_status', {'error': 'Engine not connected'}, room=sid, namespace='/gui-socket')
                return
            payload['user_context'] = {'id': user_id, 'tier': 'architect'}
            payload = _inject_fac_if_needed(session, user_id, eng_id, payload)
            sio.emit('request_ai_status', {'v': 2, 'payload': payload}, room=eng_sid, namespace='/engine-socket')
        finally:
            session.close()

    @sio.on('request_datasets_list', namespace='/gui-socket')
    def on_request_datasets_list(data):
        sid = request.sid
        gui_sess = _safe_get_session(sid, namespace='/gui-socket')
        if gui_sess is None: return
        user_id = gui_sess.get('user_id')
        if not isinstance(data, dict) or data.get('v') != 2: return
        payload = data.get('payload', {})
        target_engine_id = payload.get('target_engine_id')
        session = get_db_session()
        try:
            eng_id, eng_sid = _resolve_target_engine_sid(session, user_id, target_engine_id)
            if not eng_id or not eng_sid:
                sio.emit('response_datasets_list', {'error': 'Engine not connected'}, room=sid, namespace='/gui-socket')
                return
            payload['user_context'] = {'id': user_id, 'tier': 'architect'}
            payload = _inject_fac_if_needed(session, user_id, eng_id, payload)
            sio.emit('request_datasets_list', {'v': 2, 'payload': payload}, room=eng_sid, namespace='/engine-socket')
        finally:
            session.close()

    @sio.on('request_local_models', namespace='/gui-socket')
    def on_request_local_models(data):
        sid = request.sid
        gui_sess = _safe_get_session(sid, namespace='/gui-socket')
        if gui_sess is None: return
        user_id = gui_sess.get('user_id')
        if not isinstance(data, dict) or data.get('v') != 2: return
        payload = data.get('payload', {})
        target_engine_id = payload.get('target_engine_id')
        session = get_db_session()
        try:
            eng_id, eng_sid = _resolve_target_engine_sid(session, user_id, target_engine_id)
            if not eng_id or not eng_sid:
                sio.emit('response_local_models', {'error': 'Engine not connected'}, room=sid, namespace='/gui-socket')
                return
            payload['user_context'] = {'id': user_id, 'tier': 'architect'}
            payload = _inject_fac_if_needed(session, user_id, eng_id, payload)
            sio.emit('request_local_models', {'v': 2, 'payload': payload}, room=eng_sid, namespace='/engine-socket')
        finally:
            session.close()

    @sio.on('request_training_job_status', namespace='/gui-socket')
    def on_request_training_job_status(data):
        sid = request.sid
        gui_sess = _safe_get_session(sid, namespace='/gui-socket')
        if gui_sess is None: return
        user_id = gui_sess.get('user_id')
        if not isinstance(data, dict) or data.get('v') != 2: return
        payload = data.get('payload', {})
        target_engine_id = payload.get('target_engine_id')
        session = get_db_session()
        try:
            eng_id, eng_sid = _resolve_target_engine_sid(session, user_id, target_engine_id)
            if not eng_id or not eng_sid:
                sio.emit('response_training_job_status', {'error': 'Engine not connected'}, room=sid, namespace='/gui-socket')
                return
            payload['user_context'] = {'id': user_id, 'tier': 'architect'}
            payload = _inject_fac_if_needed(session, user_id, eng_id, payload)
            sio.emit('request_training_job_status', {'v': 2, 'payload': payload}, room=eng_sid, namespace='/engine-socket')
        finally:
            session.close()

    @sio.on('save_preset', namespace='/gui-socket')
    def on_save_preset(data):
        app = current_app._get_current_object()
        sid = request.sid
        gui_sess = _safe_get_session(sid, namespace='/gui-socket')
        if gui_sess is None: return
        user_id = gui_sess.get('user_id')
        user_addr = gui_sess.get('user_address')
        if not isinstance(data, dict) or data.get('v') != 2: return
        payload = data.get('payload', {})
        target_engine_id = payload.get('target_engine_id')
        session = get_db_session()
        try:
            eng_id, eng_sid = _resolve_target_engine_sid(session, user_id, target_engine_id)
            if not eng_id or not eng_sid:
                sio.emit('notification', {'text': 'Engine offline', 'color': 'error'}, room=sid, namespace='/gui-socket')
                return
            payload['user_context'] = {'id': user_id, 'tier': 'architect'}
            payload['user_context']['public_address'] = user_addr
            payload = _inject_fac_if_needed(session, user_id, eng_id, payload)
            sio.emit('save_preset', {'v': 2, 'payload': payload}, room=eng_sid, namespace='/engine-socket')
            app.logger.info(f"[Gateway] Fwd 'save_preset' GUI {sid} -> EngineSID {eng_sid} (EngineID: {eng_id})")
        except Exception as e:
            app.logger.error(f"[Gateway] Error forwarding 'save_preset': {e}", exc_info=True)
        finally:
            session.close()

    @sio.on('delete_preset', namespace='/gui-socket')
    def on_delete_preset(data):
        app = current_app._get_current_object()
        sid = request.sid
        gui_sess = _safe_get_session(sid, namespace='/gui-socket')
        if gui_sess is None: return
        user_id = gui_sess.get('user_id')
        if not isinstance(data, dict) or data.get('v') != 2: return
        payload = data.get('payload', {})
        target_engine_id = payload.get('target_engine_id')
        payload['user_context'] = {'id': user_id, 'tier': 'architect'}
        session = get_db_session()
        try:
            eng_id, eng_sid = _resolve_target_engine_sid(session, user_id, target_engine_id)
            if not eng_id or not eng_sid:
                sio.emit('response_presets_list', {'error': f'Engine {target_engine_id or "active"} is not connected.'}, room=sid, namespace='/gui-socket')
                return
            payload = _inject_fac_if_needed(session, user_id, eng_id, payload)
            sio.emit('delete_preset', {'v': 2, 'payload': payload}, room=eng_sid, namespace='/engine-socket')
            app.logger.info(f"[Gateway] Fwd 'delete_preset' GUI {sid} -> EngineSID {eng_sid} (EngineID: {eng_id})")
        except Exception as e:
            app.logger.error(f"[Gateway] Error forwarding 'delete_preset': {e}", exc_info=True)
        finally:
            session.close()

    @sio.on('load_preset', namespace='/gui-socket')
    def on_load_preset(data):
        app = current_app._get_current_object()
        sid = request.sid
        gui_sess = _safe_get_session(sid, namespace='/gui-socket')
        if gui_sess is None: return
        user_id = gui_sess.get('user_id')
        if not isinstance(data, dict) or data.get('v') != 2: return
        payload = data.get('payload', {})
        target_engine_id = payload.get('target_engine_id')
        share_token = payload.get('share_token')
        session = get_db_session()
        try:
            if share_token:
                eng_id, eng_sid, owner_id = _resolve_sid_via_share_token(session, share_token)
                if eng_id and eng_sid:
                    payload['_target_user_id'] = user_id
                    payload['user_context'] = {'id': owner_id, 'tier': 'architect'}
                    sio.emit('request_load_preset', {'v': 2, 'payload': payload}, room=eng_sid, namespace='/engine-socket')
                    app.logger.info(f"[Gateway] Fwd 'load_preset' (Shared Token) -> EngineSID {eng_sid}")
                    return
                else:
                    sio.emit('response_load_preset', {'error': f'Shared Engine is offline or token invalid.'}, room=sid, namespace='/gui-socket')
                    return
            eng_id, eng_sid = _resolve_target_engine_sid(session, user_id, target_engine_id)
            if not eng_id or not eng_sid:
                sio.emit('response_load_preset', {'error': f'Engine {target_engine_id or "active"} is not connected.'}, room=sid, namespace='/gui-socket')
                return
            engine = session.query(RegisteredEngine).filter_by(id=eng_id).first()
            if engine and str(engine.user_id) != str(user_id):
                 payload['_target_user_id'] = user_id
                 payload['user_context'] = {'id': engine.user_id, 'tier': 'architect'}
            else:
                payload['user_context'] = {'id': user_id, 'tier': 'architect'}
            payload = _inject_fac_if_needed(session, user_id, eng_id, payload)
            sio.emit('request_load_preset', {'v': 2, 'payload': payload}, room=eng_sid, namespace='/engine-socket')
            app.logger.info(f"[Gateway] Fwd 'request_load_preset' GUI {sid} -> EngineSID {eng_sid} (EngineID: {eng_id})")
        except Exception as e:
            app.logger.error(f"[Gateway] Error forwarding 'load_preset': {e}", exc_info=True)
        finally:
            session.close()

    @sio.on('install_component', namespace='/gui-socket')
    def on_install_component(data):
        app = current_app._get_current_object()
        sid = request.sid
        gui_sess = _safe_get_session(sid, namespace='/gui-socket')
        if gui_sess is None: return
        user_id = gui_sess.get('user_id')
        if not isinstance(data, dict) or data.get('v') != 2: return
        payload = data.get('payload')
        if payload.get('component_type') == 'widgets':
            payload['component_type'] = 'apps'
        target_engine_id = payload.get('target_engine_id')
        session = get_db_session()
        try:
            eng_id, eng_sid = _resolve_target_engine_sid(session, user_id, target_engine_id)
            if not eng_id or not eng_sid:
                sio.emit('component_install_status', {'v': 2, 'payload': {
                    'error': f'Engine {target_engine_id or "active"} is not connected.',
                    'success': False,
                    'component_id': payload.get('component_id'),
                    'component_type': payload.get('component_type'),
                    'message': 'Engine is not connected to the Gateway.'
                }}, room=sid, namespace='/gui-socket')
                return
            payload['user_context'] = {'id': user_id, 'tier': 'architect'}
            payload = _inject_fac_if_needed(session, user_id, eng_id, payload)
            sio.emit('install_component', {'v': 2, 'payload': payload}, room=eng_sid, namespace='/engine-socket')
            app.logger.info(f"[Gateway] Fwd 'install_component' GUI {sid} -> EngineSID {eng_sid} (EngineID: {eng_id})")
        finally:
            session.close()

    @sio.on('uninstall_component', namespace='/gui-socket')
    def on_uninstall_component(data):
        app = current_app._get_current_object()
        sid = request.sid
        gui_sess = _safe_get_session(sid, namespace='/gui-socket')
        if gui_sess is None: return
        user_id = gui_sess.get('user_id')
        if not isinstance(data, dict) or data.get('v') != 2: return
        payload = data.get('payload')
        if payload.get('component_type') == 'widgets':
            payload['component_type'] = 'apps'
        target_engine_id = payload.get('target_engine_id')
        session = get_db_session()
        try:
            eng_id, eng_sid = _resolve_target_engine_sid(session, user_id, target_engine_id)
            if not eng_id or not eng_sid:
                sio.emit('component_install_status', {'v': 2, 'payload': {
                    'error': f'Engine {target_engine_id or "active"} is not connected.',
                    'success': False,
                    'component_id': payload.get('component_id'),
                    'component_type': payload.get('component_type'),
                    'message': 'Engine is not connected to the Gateway.'
                }}, room=sid, namespace='/gui-socket')
                return
            payload['user_context'] = {'id': user_id, 'tier': 'architect'}
            payload = _inject_fac_if_needed(session, user_id, eng_id, payload)
            sio.emit('uninstall_component', {'v': 2, 'payload': payload}, room=eng_sid, namespace='/engine-socket')
            app.logger.info(f"[Gateway] Fwd 'uninstall_component' GUI {sid} -> EngineSID {eng_sid} (EngineID: {eng_id})")
        finally:
            session.close()