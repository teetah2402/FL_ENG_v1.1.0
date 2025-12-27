from flask import request, current_app
from app.helpers import get_db_session
from app.models import RegisteredEngine
from .utils import _safe_get_session, _resolve_target_engine_sid, _resolve_sid_via_share_token, _inject_fac_if_needed, g_job_ownership, g_execution_ownership

def register_handlers(sio):

    @sio.on('execute_workflow', namespace='/gui-socket')
    def on_execute_workflow(data):
        app = current_app._get_current_object()
        sid = request.sid
        gui_sess = _safe_get_session(sid, namespace='/gui-socket')
        if gui_sess is None:
            app.logger.warning(f"[Gateway] 'execute_workflow' from unauthenticated SID {sid}.")
            return

        user_id = gui_sess.get('user_id')
        if not isinstance(data, dict) or data.get('v') != 2:
            app.logger.error(f"[Core] Non-versioned 'execute_workflow' from GUI {sid}.")
            return
        payload = data.get('payload', {})
        target_engine_id = payload.get('target_engine_id')
        job_id = payload.get('job_id')

        if job_id:
            g_job_ownership[job_id] = user_id
            g_execution_ownership[job_id] = user_id

        session = get_db_session()
        try:
            eng_id, eng_sid = _resolve_target_engine_sid(session, user_id, target_engine_id)
            if not eng_id or not eng_sid:
                app.logger.warning(f"[Gateway] Cannot forward 'execute_workflow'. No LIVE SID for engine {target_engine_id or 'default active'}.")
                return

            payload['user_context'] = {'id': user_id, 'tier': 'architect'}
            payload['_target_user_id'] = user_id
            payload = _inject_fac_if_needed(session, user_id, eng_id, payload)

            sio.emit('execute_workflow', {'v': 2, 'payload': payload}, room=eng_sid, namespace='/engine-socket')
            app.logger.info(f"[Gateway] Fwd 'execute_workflow' GUI {sid} -> EngineSID {eng_sid} (EngineID: {eng_id})")

        except Exception as e:
            app.logger.error(f"[Gateway] Error forwarding 'execute_workflow': {e}", exc_info=True)
        finally:
            session.close()

    @sio.on('execute_standalone_node', namespace='/gui-socket')
    def on_execute_standalone_node(data):
        app = current_app._get_current_object()
        sid = request.sid
        gui_sess = _safe_get_session(sid, namespace='/gui-socket')
        if gui_sess is None:
            app.logger.warning(f"[Gateway] 'execute_standalone_node' from unauthenticated SID {sid}.")
            return

        user_id = gui_sess.get('user_id')
        if not isinstance(data, dict) or data.get('v') != 2:
            app.logger.error(f"[Core] Non-versioned 'execute_standalone_node' from GUI {sid}.")
            return
        payload = data.get('payload', {})
        target_engine_id = payload.get('target_engine_id')
        share_token = payload.get('share_token')
        job_id = payload.get('job_id')

        if job_id:
            g_job_ownership[job_id] = user_id
            g_execution_ownership[job_id] = user_id

        session = get_db_session()
        try:
            if share_token:
                eng_id, eng_sid, owner_id = _resolve_sid_via_share_token(session, share_token)
                if eng_id and eng_sid:
                    payload['user_context'] = {'id': owner_id, 'tier': 'architect'}
                    payload['_target_user_id'] = user_id
                    payload = _inject_fac_if_needed(session, user_id, eng_id, payload)

                    sio.emit('execute_standalone_node', {'v': 2, 'payload': payload}, room=eng_sid, namespace='/engine-socket')
                    app.logger.info(f"[Gateway] Fwd 'execute_standalone_node' (Shared Token) -> EngineSID {eng_sid}")
                    return

            eng_id, eng_sid = _resolve_target_engine_sid(session, user_id, target_engine_id)
            if not eng_id or not eng_sid:
                app.logger.warning(f"[Gateway] Cannot forward 'execute_standalone_node'. No LIVE SID for engine {target_engine_id or 'default active'}.")
                return

            payload['user_context'] = {'id': user_id, 'tier': 'architect'}
            payload['_target_user_id'] = user_id
            payload = _inject_fac_if_needed(session, user_id, eng_id, payload)

            sio.emit('execute_standalone_node', {'v': 2, 'payload': payload}, room=eng_sid, namespace='/engine-socket')
            app.logger.info(f"[Gateway] Fwd 'execute_standalone_node' GUI {sid} -> EngineSID {eng_sid} (EngineID: {eng_id})")

        except Exception as e:
            app.logger.error(f"[Gateway] Error forwarding 'execute_standalone_node': {e}", exc_info=True)
        finally:
            session.close()

    @sio.on('stop_workflow', namespace='/gui-socket')
    def on_stop_workflow(data):
        app = current_app._get_current_object()
        sid = request.sid
        gui_sess = _safe_get_session(sid, namespace='/gui-socket')
        if gui_sess is None:
            app.logger.warning(f"[Gateway] 'stop_workflow' from unauthenticated SID {sid}.")
            return

        user_id = gui_sess.get('user_id')
        if not isinstance(data, dict) or data.get('v') != 2:
            app.logger.error(f"[Core] Non-versioned 'stop_workflow' from GUI {sid}.")
            return
        payload = data.get('payload', {})
        target_engine_id = payload.get('target_engine_id')

        session = get_db_session()
        try:
            eng_id, eng_sid = _resolve_target_engine_sid(session, user_id, target_engine_id)
            if not eng_id or not eng_sid:
                app.logger.warning(f"[Gateway] Cannot forward 'stop_workflow'. No LIVE SID for engine {target_engine_id or 'default active'}.")
                return

            payload['user_context'] = {'id': user_id, 'tier': 'architect'}
            payload = _inject_fac_if_needed(session, user_id, eng_id, payload)
            sio.emit('stop_workflow', {'v': 2, 'payload': payload}, room=eng_sid, namespace='/engine-socket')
            app.logger.info(f"[Gateway] Fwd 'stop_workflow' GUI {sid} -> EngineSID {eng_sid} (EngineID: {eng_id})")

        except Exception as e:
            app.logger.error(f"[Gateway] Error forwarding 'stop_workflow': {e}", exc_info=True)
        finally:
            session.close()

    @sio.on('pause_workflow', namespace='/gui-socket')
    def on_pause_workflow(data):
        app = current_app._get_current_object()
        sid = request.sid
        gui_sess = _safe_get_session(sid, namespace='/gui-socket')
        if gui_sess is None:
            app.logger.warning(f"[Gateway] 'pause_workflow' from unauthenticated SID {sid}.")
            return

        user_id = gui_sess.get('user_id')
        if not isinstance(data, dict) or data.get('v') != 2:
            app.logger.error(f"[Core] Non-versioned 'pause_workflow' from GUI {sid}.")
            return
        payload = data.get('payload', {})
        target_engine_id = payload.get('target_engine_id')

        session = get_db_session()
        try:
            eng_id, eng_sid = _resolve_target_engine_sid(session, user_id, target_engine_id)
            if not eng_id or not eng_sid:
                app.logger.warning(f"[Gateway] Cannot forward 'pause_workflow'. No LIVE SID for engine {target_engine_id or 'default active'}.")
                return

            payload['user_context'] = {'id': user_id, 'tier': 'architect'}
            payload = _inject_fac_if_needed(session, user_id, eng_id, payload)
            sio.emit('pause_workflow', {'v': 2, 'payload': payload}, room=eng_sid, namespace='/engine-socket')
            app.logger.info(f"[Gateway] Fwd 'pause_workflow' GUI {sid} -> EngineSID {eng_sid} (EngineID: {eng_id})")

        except Exception as e:
            app.logger.error(f"[Gateway] Error forwarding 'pause_workflow': {e}", exc_info=True)
        finally:
            session.close()