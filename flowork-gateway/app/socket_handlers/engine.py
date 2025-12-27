from flask import request, current_app
from datetime import datetime
from app.models import RegisteredEngine, UserEngineSession
from app.globals import globals_instance
from app.helpers import get_db_session, find_active_engine_session
from .utils import _safe_get_session, _broadcast_response, _emit_to_gui, g_engine_active_job, g_execution_ownership, g_job_ownership

def register_handlers(sio):

    @sio.on('engine_ready', namespace='/engine-socket')
    def handle_engine_ready(data):
        app = current_app._get_current_object()
        sid = request.sid
        session_data = _safe_get_session(sid, namespace='/engine-socket')

        if session_data is None:
            app.logger.warning(f"[Gateway Engine Ready] 'engine_ready' from SID {sid} with no session data. Ignoring.")
            return

        engine_id = session_data.get('engine_id')
        user_id = session_data.get('user_id')

        internal_api_url = None
        if isinstance(data, dict) and data.get('v') == 2:
            internal_api_url = (data.get('payload') or {}).get('internal_api_url')
        elif isinstance(data, dict):
            internal_api_url = data.get('internal_api_url')

        if not internal_api_url:
            app.logger.warning(f"[Gateway Engine Ready] Engine {engine_id} sent without internal_api_url.")

        app.logger.info(f"[Gateway Engine Ready] Engine {engine_id} READY. Internal URL: {internal_api_url}")

        globals_instance.engine_manager.active_engine_sessions[engine_id] = sid
        if internal_api_url:
            globals_instance.engine_manager.engine_url_map[engine_id] = internal_api_url

        session = get_db_session()
        try:
            for stale in session.query(UserEngineSession).filter_by(engine_id=engine_id, is_active=True).all():
                stale.is_active = False

            new_session = UserEngineSession(
                user_id=user_id,
                engine_id=engine_id,
                internal_url=internal_api_url,
                is_active=True,
                last_activated_at=int(datetime.utcnow().timestamp())
            )
            session.add(new_session)
            session.commit()

            _broadcast_response(engine_id, 'engine_status_update', {
                'engine_id': engine_id,
                'status': 'online',
                'vitals': None
            })

        except Exception as e:
            app.logger.error(f"[Gateway Engine Ready] Failed to update session for engine {engine_id}: {e}", exc_info=True)
            session.rollback()
        finally:
            session.close()

    @sio.on('engine_vitals_update', namespace='/engine-socket')
    def handle_engine_vitals_update(data=None):
        app = current_app._get_current_object()
        sid = request.sid
        sess = _safe_get_session(sid, namespace='/engine-socket')

        payload = {}
        if isinstance(data, dict) and data.get('v') == 2:
            payload = data.get('payload') or {}
        elif isinstance(data, dict):
            payload = data
        else:
            payload = {}

        engine_id = (sess or {}).get('engine_id') or payload.get('engine_id')
        user_id = (sess or {}).get('user_id') or payload.get('user_id')
        internal_url = payload.get('internal_api_url') or payload.get('internal_url')

        if not engine_id or not user_id:
            app.logger.warning(f"[Gateway Vitals] Missing engine_id/user_id (sid={sid}). Dropping vitals.")
            return

        globals_instance.engine_manager.active_engine_sessions[str(engine_id)] = sid

        current_sid = globals_instance.engine_manager.active_engine_sessions.get(engine_id)
        did_backfill = False

        if current_sid != sid:
            globals_instance.engine_manager.active_engine_sessions[engine_id] = sid
            did_backfill = True
            app.logger.info(f"[Gateway Vitals] Backfilled live SID map for Engine {engine_id} -> {sid}")

        if internal_url:
            globals_instance.engine_manager.engine_url_map[engine_id] = internal_url

        session = get_db_session()
        try:
            active_db = find_active_engine_session(session, user_id, engine_id)
            if not active_db:
                for stale in session.query(UserEngineSession).filter_by(engine_id=engine_id, is_active=True).all():
                    stale.is_active = False

                new_sess = UserEngineSession(
                    user_id=user_id,
                    engine_id=engine_id,
                    internal_url=internal_url or globals_instance.engine_manager.engine_url_map.get(engine_id),
                    is_active=True,
                    last_activated_at=int(datetime.utcnow().timestamp())
                )
                session.add(new_sess)
                session.commit()
                did_backfill = True
                app.logger.info(f"[Gateway Vitals] Backfilled ACTIVE DB session for engine {engine_id}")
        except Exception as e:
            app.logger.error(f"[Gateway Vitals] Backfill DB session failed for engine {engine_id}: {e}", exc_info=True)
            session.rollback()
        finally:
            session.close()

        if did_backfill:
            _broadcast_response(engine_id, 'engine_status_update', {
                'engine_id': engine_id,
                'status': 'online',
                'vitals': None
            })

        _broadcast_response(engine_id, 'engine_vitals_update', {
            'engine_id': engine_id,
            'vitals': payload
        })

    @sio.on('forward_event_to_gui', namespace='/engine-socket')
    def on_forward_event_to_gui(data):
        """
        Central Handler for forwarding events from Engine -> GUI.
        """
        app = current_app._get_current_object()

        try:
            sess = _safe_get_session(request.sid, namespace='/engine-socket')
            if sess and sess.get('engine_id'):
                eid = sess.get('engine_id')
                if globals_instance.engine_manager.active_engine_sessions.get(eid) != request.sid:
                     globals_instance.engine_manager.active_engine_sessions[eid] = request.sid
        except Exception:
            pass

        if not isinstance(data, dict) or data.get('v') != 2:
            app.logger.warning(f"[Gateway] Received non-v2 'forward_event_to_gui'. Ignoring.")
            return

        payload = data.get('payload', {})
        event_name = payload.get("event_name")
        event_data = payload.get("event_data") or {}
        user_id = payload.get("user_id") # Engine Session Owner ID

        if not event_name:
            app.logger.warning(f"[Gateway] Invalid 'forward_event_to_gui' payload: {data}")
            return

        if event_name == 'WIDGETS_RELOADED':
            event_name = 'APPS_RELOADED'

        sess = _safe_get_session(request.sid, namespace='/engine-socket')
        current_engine_id = sess.get('engine_id') if sess else None

        if not current_engine_id and 'engine_id' in event_data:
              current_engine_id = event_data['engine_id']

        if current_engine_id and isinstance(event_data, dict) and 'engine_id' not in event_data:
            event_data['engine_id'] = current_engine_id


        target_user_id = event_data.get('_target_user_id')
        if not target_user_id:
            target_user_id = (event_data.get('payload') or {}).get('_target_user_id')

        job_id = event_data.get('job_id')
        execution_id = event_data.get('execution_id')

        if event_name == 'WORKFLOW_EXECUTION_UPDATE':
            status = event_data.get('status') or (event_data.get('status_data') or {}).get('status')
            if status == 'RUNNING' and current_engine_id and job_id:
                g_engine_active_job[current_engine_id] = job_id
                if execution_id and g_execution_ownership.get(execution_id):
                    g_job_ownership[job_id] = g_execution_ownership[execution_id]

        if not job_id and current_engine_id:
            inferred_job_id = g_engine_active_job.get(current_engine_id)
            if inferred_job_id:
                job_id = inferred_job_id

        if not target_user_id and execution_id and g_execution_ownership.get(execution_id):
              target_user_id = g_execution_ownership[execution_id]

        if not target_user_id and job_id and g_job_ownership.get(job_id):
            target_user_id = g_job_ownership[job_id]

        if not target_user_id and job_id and g_execution_ownership.get(job_id):
              target_user_id = g_execution_ownership[job_id]

        BROADCAST_EVENTS = {
            'JOB_COMPLETED_CHECK',
            'WORKFLOW_EXECUTION_UPDATE',
            'EXECUTION_STARTED',
            'EXECUTION_PROGRESS',
            'node_status_update',
            'engine_status_update',
            'APPS_RELOADED',
            'settings_state'
        }

        STRICT_UNICAST_EVENTS = {
            'SHOW_DEBUG_POPUP',
            'WORKFLOW_LOG_ENTRY',
            'gui:input',
            'FILESYSTEM_LIST_RESPONSE'
        }

        if event_name in BROADCAST_EVENTS:
            if current_engine_id:
                _broadcast_response(current_engine_id, event_name, event_data)
            elif user_id:
                sio.emit(event_name, event_data, room=str(user_id), namespace='/gui-socket')

            if target_user_id and str(target_user_id) != str(user_id):
                 sio.emit(event_name, event_data, room=str(target_user_id), namespace='/gui-socket')

        elif event_name in STRICT_UNICAST_EVENTS:
            if target_user_id:
                sio.emit(event_name, event_data, room=str(target_user_id), namespace='/gui-socket')
            else:
                app.logger.warning(f"[Gateway] Blocked leakage of private event '{event_name}'. No valid target_user_id found via Job/Execution/SmartEngine registry. (Job: {job_id})")

        else:
            if target_user_id:
                sio.emit(event_name, event_data, room=str(target_user_id), namespace='/gui-socket')