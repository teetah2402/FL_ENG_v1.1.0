from flask import request, current_app
from flask_socketio import join_room, leave_room
from werkzeug.security import check_password_hash
from datetime import datetime
from app.models import AgentSession, Episode, EngineShare
from app.globals import globals_instance
from app.helpers import get_db_session
from .utils import _safe_get_session, _redact_content

def register_handlers(sio):

    @sio.on('gui:join', namespace='/gui-socket')
    def on_gui_join_session(data):
        app = current_app._get_current_object()
        sid = request.sid

        gui_sess = _safe_get_session(sid, namespace='/gui-socket')
        if not gui_sess or not gui_sess.get('user_id'):
            app.logger.warning(f"[GUI Join] SID {sid} tried to join session but is not authenticated (no Web3 connect).")
            return {'ok': False, 'error': 'Socket not authenticated'}

        user_id = gui_sess.get('user_id')

        if not isinstance(data, dict):
            app.logger.warning(f"[GUI Join] User {user_id} (SID {sid}) sent invalid join data.")
            return {'ok': False, 'error': 'Invalid payload format'}

        session_id = data.get('session_id')
        ws_token = data.get('ws_token')

        if not session_id or not ws_token:
            app.logger.warning(f"[GUI Join] User {user_id} (SID {sid}) sent incomplete join data.")
            return {'ok': False, 'error': 'session_id and ws_token are required'}

        session = get_db_session()
        try:
            agent_session = session.query(AgentSession).filter_by(id=session_id).first()

            if not agent_session:
                app.logger.warning(f"[GUI Join] User {user_id} (SID {sid}) tried to join non-existent session {session_id}.")
                return {'ok': False, 'error': 'Session not found'}

            is_owner = (agent_session.user_id == user_id)
            has_share_access = False

            if not is_owner:
                share = session.query(EngineShare).filter_by(
                    engine_id=agent_session.engine_id,
                    user_id=user_id
                ).first()
                if share:
                    has_share_access = True
                    app.logger.info(f"[GUI Join] User {user_id} is Guest via Share (Role: {share.role}). allowing access.")

            if not is_owner and not has_share_access:
                app.logger.warning(f"[AuthZ] DENIED: User {user_id} (SID {sid}) tried to join session {session_id} owned by {agent_session.user_id} without share.")
                return {'ok': False, 'error': 'Permission denied'}

            if is_owner and not check_password_hash(agent_session.ws_token_hash, ws_token):
                 app.logger.warning(f"[AuthZ] DENIED: User {user_id} (SID {sid}) provided invalid ws_token for session {session_id}.")
                 return {'ok': False, 'error': 'Invalid session token'}

            join_room(session_id, sid, namespace='/gui-socket')

            gui_sess['gui_session_id'] = session_id
            sio.server.save_session(sid, gui_sess, namespace='/gui-socket')

            app.logger.info(f"[GUI Join] SUCCESS: User {user_id} (SID {sid}) joined agent session room '{session_id}'.")
            return {'ok': True}

        except Exception as e:
            app.logger.error(f"[GUI Join] Error joining session {session_id}: {e}", exc_info=True)
            return {'ok': False, 'error': 'Internal server error'}
        finally:
            session.close()

    @sio.on('gui:input', namespace='/gui-socket')
    def on_gui_input(data):
        app = current_app._get_current_object()
        sid = request.sid

        gui_sess = _safe_get_session(sid, namespace='/gui-socket')
        if not gui_sess or not gui_sess.get('user_id'):
            app.logger.warning(f"[GUI Input] SID {sid} sent input but is not authenticated (no Web3 connect).")
            return

        session_id = gui_sess.get('gui_session_id')
        if not session_id:
            app.logger.warning(f"[GUI Input] User {gui_sess.get('user_id')} (SID {sid}) sent input without joining a session first.")
            return

        if not isinstance(data, dict):
            app.logger.warning(f"[GUI Input] SID {sid} sent invalid input data for session {session_id}.")
            return

        session = get_db_session()
        try:
            agent_session = session.query(AgentSession).filter_by(id=session_id).first()
            if not agent_session:
                app.logger.error(f"[GUI Input] SID {sid} sent input for non-existent session {session_id}.")
                return

            if agent_session.status != 'running':
                app.logger.warning(f"[GUI Input] SID {sid} sent input, but session {session_id} is not 'running' (status: {agent_session.status}). Ignoring.")
                sio.emit('agent:error', {
                    'session_id': session_id,
                    'code': 'SESSION_NOT_RUNNING',
                    'message': f'Cannot send input, session status is: {agent_session.status}'
                }, room=session_id, namespace='/gui-socket')
                return

            engine_id = agent_session.engine_id

            engine_sid = globals_instance.engine_manager.active_engine_sessions.get(str(engine_id))
            if not engine_sid:
                app.logger.error(f"[GUI Input] Cannot forward input for session {session_id}. Engine {engine_id} is OFFLINE.")
                sio.emit('agent:error', {
                    'session_id': session_id,
                    'code': 'ENGINE_OFFLINE',
                    'message': 'Engine is offline. Cannot process input.'
                }, room=session_id, namespace='/gui-socket')
                return

            payload_content = data.get('text') or data.get('tool')
            if not payload_content:
                app.logger.warning(f"[GUI Input] SID {sid} sent empty input for session {session_id}.")
                return

            core_payload = {
                "type": "input",
                "session_id": session_id,
                "payload": {
                    "text": data.get('text'),
                    "tool": data.get('tool')
                }
            }

            sio.emit(
                'gw:agent_input',
                core_payload,
                room=engine_id,
                namespace='/core-socket'
            )
            app.logger.info(f"[GUI Input] Fwd input for session {session_id} -> Engine {engine_id} (SID {engine_sid})")

        except Exception as e:
            app.logger.error(f"[GUI Input] Error forwarding input for session {session_id}: {e}", exc_info=True)
        finally:
            session.close()

    @sio.on('core:agent_status', namespace='/engine-socket')
    def on_core_agent_status(data):
        app = current_app._get_current_object()
        if not isinstance(data, dict) or 'session_id' not in data or 'phase' not in data:
            app.logger.warning(f"[Core Event] Received invalid 'core:agent_status': {data}")
            return

        session_id = data.get('session_id')
        phase = data.get('phase')
        app.logger.info(f"[Core Event] Received status for session {session_id}: {phase}")

        session = get_db_session()
        try:
            agent_session = session.query(AgentSession).filter_by(id=session_id).first()
            if agent_session:
                agent_session.status = phase
                session.commit()
            else:
                app.logger.warning(f"[Core Event] Received status for unknown session {session_id}")
        except Exception as e:
            app.logger.error(f"[Core Event] DBError updating status for session {session_id}: {e}", exc_info=True)
            session.rollback()
        finally:
            session.close()

        gui_payload = {
            'session_id': session_id,
            'phase': phase
        }
        sio.emit('agent:status', gui_payload, room=session_id, namespace='/gui-socket')

    @sio.on('core:agent_token', namespace='/engine-socket')
    def on_core_agent_token(data):
        app = current_app._get_current_object()
        if not isinstance(data, dict) or 'session_id' not in data or 'text' not in data:
            app.logger.warning(f"[Core Event] Received invalid 'core:agent_token': {data}")
            return

        session_id = data.get('session_id')
        raw_text = data.get('text')
        redacted_text = _redact_content(raw_text)

        gui_payload = {
            'session_id': session_id,
            'chunk': redacted_text
        }
        sio.emit('agent:token', gui_payload, room=session_id, namespace='/gui-socket')

    @sio.on('core:agent_tool', namespace='/engine-socket')
    def on_core_agent_tool(data):
        app = current_app._get_current_object()
        if not isinstance(data, dict) or 'session_id' not in data:
            app.logger.warning(f"[Core Event] Received invalid 'core:agent_tool': {data}")
            return
        session_id = data.get('session_id')
        app.logger.info(f"[Core Event] Received tool call for session {session_id}: {data.get('name')}")
        sio.emit('agent:tool', data, room=session_id, namespace='/gui-socket')

    @sio.on('core:agent_done', namespace='/engine-socket')
    def on_core_agent_done(data):
        app = current_app._get_current_object()
        if not isinstance(data, dict) or 'session_id' not in data:
            app.logger.warning(f"[Core Event] Received invalid 'core:agent_done': {data}")
            return

        session_id = data.get('session_id')
        app.logger.info(f"[Core Event] Received DONE for session {session_id}")

        session = get_db_session()
        try:
            agent_session = session.query(AgentSession).filter_by(id=session_id).first()
            if agent_session:
                agent_session.status = 'done'
                agent_session.finished_at = datetime.utcnow()

                episode_id = data.get('episode_id')
                timeline_ptr = data.get('timeline_ptr')

                if episode_id:
                    agent_session.episode_id = episode_id
                    episode = session.query(Episode).filter_by(id=episode_id).first()
                    if episode and timeline_ptr:
                        episode.core_timeline_ptr = timeline_ptr

                session.commit()
            else:
                app.logger.warning(f"[Core Event] Received done for unknown session {session_id}")
        except Exception as e:
            app.logger.error(f"[Core Event] DBError updating done status for session {session_id}: {e}", exc_info=True)
            session.rollback()
        finally:
            session.close()

        sio.emit('agent:done', data, room=session_id, namespace='/gui-socket')

    @sio.on('core:agent_error', namespace='/engine-socket')
    def on_core_agent_error(data):
        app = current_app._get_current_object()
        if not isinstance(data, dict) or 'session_id' not in data:
            app.logger.warning(f"[Core Event] Received invalid 'core:agent_error': {data}")
            return

        session_id = data.get('session_id')
        app.logger.error(f"[Core Event] Received ERROR for session {session_id}: {data.get('code')} - {data.get('message')}")

        session = get_db_session()
        try:
            agent_session = session.query(AgentSession).filter_by(id=session_id).first()
            if agent_session:
                agent_session.status = 'error'
                agent_session.finished_at = datetime.utcnow()
                session.commit()
            else:
                app.logger.warning(f"[Core Event] Received error for unknown session {session_id}")
        except Exception as e:
            app.logger.error(f"[Core Event] DBError updating error status for session {session_id}: {e}", exc_info=True)
            session.rollback()
        finally:
            session.close()

        sio.emit('agent:error', data, room=session_id, namespace='/gui-socket')