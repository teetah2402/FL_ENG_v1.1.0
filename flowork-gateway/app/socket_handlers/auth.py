########################################################################
# WEBSITE https://flowork.cloud
# File NAME : C:\FLOWORK\flowork-gateway\app\socket_handlers\auth.py
# DESCRIPTION: Auth Handler (Fixed Import Path)
########################################################################

import os
from flask import request, current_app
from flask_socketio import join_room, leave_room
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
import json
import uuid
import secrets
from app.models import RegisteredEngine, UserEngineSession, AgentSession, User, EngineShare
from app.globals import globals_instance
from app.helpers import get_db_session, verify_web3_signature
# [FIX] Import utils from sibling module (.), not parent (..)
from .utils import _safe_get_session, _broadcast_response
from sqlalchemy.orm import joinedload

def register_handlers(sio):

    @sio.on('connect', namespace='/engine-socket')
    def on_engine_connect(auth):
        app = current_app._get_current_object()
        sid = request.sid
        remote_addr = request.environ.get('REMOTE_ADDR', 'N/A')

        if not auth or 'engine_id' not in auth or 'token' not in auth:
            app.logger.warning(f"[Gateway Engine Connect] Engine connection from {remote_addr} missing auth data. Disconnecting.")
            return False

        engine_id = auth.get('engine_id')
        token = auth.get('token')

        session = get_db_session()
        try:
            engine = session.query(RegisteredEngine).filter_by(id=engine_id).first()
            if not engine or not check_password_hash(engine.engine_token_hash, token):
                app.logger.warning(f"[Gateway Engine Connect] Engine auth failed for engine_id: {engine_id} from {remote_addr}. Disconnecting.")
                sio.emit('auth_failed', {'error': 'Invalid engine_id or token'}, room=sid, namespace='/engine-socket')
                return False

            sio.server.save_session(sid, {'engine_id': engine_id, 'user_id': engine.user_id}, namespace='/engine-socket')
            join_room(engine.user_id, sid, namespace='/engine-socket')
            join_room(engine_id, sid, namespace='/engine-socket')
            app.logger.info(f"[Gateway Engine Connect] Engine {engine_id} (SID: {sid}) joined room '{engine_id}' for commands.")

            globals_instance.engine_manager.active_engine_sessions[engine_id] = sid
            app.logger.info(f"[Gateway Engine Connect] Pre-registered live SID for Engine {engine_id} -> {sid}")

            sio.emit('auth_success', {'user_id': engine.user_id}, room=sid, namespace='/engine-socket')
            return True

        except Exception as e:
            app.logger.error(f"[Gateway Engine Connect] Error during engine connect: {e}", exc_info=True)
            return False
        finally:
            session.close()

    @sio.on('disconnect', namespace='/engine-socket')
    def on_engine_disconnect():
        app = current_app._get_current_object()
        sid = request.sid
        session_data = _safe_get_session(sid, namespace='/engine-socket')

        if session_data is None:
            app.logger.warning(f"[Gateway Engine Disconnect] A disconnected engine SID {sid} had no session data.")
            return

        engine_id = session_data.get('engine_id')
        user_id = session_data.get('user_id')

        if not engine_id:
            app.logger.warning(f"[Gateway Engine Disconnect] SID {sid} missing engine_id.")
            return

        app.logger.info(f"[Gateway Engine Disconnect] Engine {engine_id} (User: {user_id}) disconnected. SID: {sid}")

        removed_sid = globals_instance.engine_manager.active_engine_sessions.pop(engine_id, None)
        if removed_sid:
            app.logger.info(f"[Gateway Engine Disconnect] Removed live SID {removed_sid} for Engine {engine_id} from active session map.")
        else:
            app.logger.warning(f"[Gateway Engine Disconnect] Engine {engine_id} disconnected, but it was not in the active session map.")

        session = get_db_session()
        try:
            existing_session = session.query(UserEngineSession).filter_by(engine_id=engine_id, is_active=True).first()
            if existing_session:
                existing_session.is_active = False
                session.commit()
                globals_instance.engine_manager.engine_url_map.pop(engine_id, None)

                _broadcast_response(engine_id, 'engine_status_update', {
                    'engine_id': engine_id,
                    'status': 'offline',
                    'vitals': None
                })

            active_agent_sessions = session.query(AgentSession).filter_by(
                engine_id=engine_id,
                status='running'
            ).all()

            if active_agent_sessions:
                app.logger.warning(f"[Gateway Engine Disconnect] Engine {engine_id} died with {len(active_agent_sessions)} active agent sessions. Marking as errored.")
                for agent_sess in active_agent_sessions:
                    agent_sess.status = 'error'
                    agent_sess.finished_at = datetime.utcnow()

                    error_payload = {
                        'session_id': agent_sess.id,
                        'code': 'ENGINE_DISCONNECT',
                        'message': 'The engine executing this session disconnected unexpectedly.'
                    }
                    sio.emit('agent:error', error_payload, room=agent_sess.id, namespace='/gui-socket')

                session.commit()

        except Exception as e:
            app.logger.error(f"[Gateway Engine Disconnect] Error updating engine session for {engine_id}: {e}", exc_info=True)
            session.rollback()
        finally:
            session.close()

    @sio.on('connect', namespace='/gui-socket')
    def on_gui_connect(auth):
        app = current_app._get_current_object()
        sid = request.sid
        remote_addr = request.environ.get('REMOTE_ADDR', 'N/A')

        if not auth:
            app.logger.info(f"[Gateway GUI Connect] Anonymous GUI client connected from {remote_addr}. SID: {sid}.")
            sio.server.save_session(sid, {'user_id': None, 'user_address': None}, namespace='/gui-socket')
            return True

        auth_dict = auth
        if isinstance(auth, str):
            try:
                auth_dict = json.loads(auth)
                app.logger.info(f"[Gateway GUI Connect] Parsed string-based auth from {remote_addr}.")
            except json.JSONDecodeError:
                app.logger.error(f"[Gateway GUI Connect] Failed to parse string-based auth from {remote_addr}.")
                return False
        elif not isinstance(auth, dict):
            app.logger.error(f"[Gateway GUI Connect] Auth object is not dict or string. Denied.")
            return False

        headers = auth_dict.get('headers') if auth_dict else None
        if not headers:
            app.logger.warning(f"[Gateway GUI] Missing signature headers from {remote_addr}. Denied.")
            return False

        address = headers.get('X-User-Address')
        message = headers.get('X-Signed-Message')
        signature = headers.get('X-Signature')
        payload_v = headers.get('X-Payload-Version')

        if not address or not message or not signature or not payload_v:
            app.logger.warning(f"[Gateway GUI] Incomplete auth headers from {remote_addr}. Denied.")
            return False

        # --- [TIMESTAMP VALIDATION WITH BYPASS] ---
        is_dev_mode = os.environ.get("FLASK_ENV") == "development" or os.environ.get("DEV_MODE") == "true"

        try:
            ts_str = message.split('|')[-1]
            if not ts_str.isdigit():
                raise ValueError("Invalid message format")

            ts = int(ts_str)
            server_ts = datetime.utcnow().timestamp()
            diff = abs(server_ts - ts)

            max_diff = 86400 if is_dev_mode else 300

            if diff > max_diff:
                app.logger.warning(f"[Gateway GUI] Auth expired for {address}. Diff: {diff}s (Max: {max_diff}s). DevMode: {is_dev_mode}. Denied.")
                return False

            if not verify_web3_signature(address, message, signature):
                app.logger.warning(f"[Gateway GUI] Invalid signature for {address} from {remote_addr}. Denied.")
                return False

        except Exception as e:
            app.logger.error(f"[Gateway GUI] Error during signature validation: {e}", exc_info=True)
            return False

        session = get_db_session()
        try:
            user = session.query(User).filter(User.public_address.ilike(address)).first()

            if not user:
                app.logger.info(f"[Gateway GUI] First-time login for {address}. Auto-provisioning new user record.")

                new_user_id = str(uuid.uuid4())
                dummy_email = f"{address.lower()}@flowork.cloud"
                dummy_password = secrets.token_urlsafe(32)

                user = User(
                    id=new_user_id,
                    username=f"user_{address[:8]}",
                    email=dummy_email,
                    password_hash=generate_password_hash(dummy_password),
                    public_address=address,
                    status='active'
                )
                session.add(user)

                try:
                    session.commit()
                    app.logger.info(f"[Gateway GUI] Successfully created new user {new_user_id} for {address}.")
                except Exception as e_commit:
                    app.logger.error(f"[Gateway GUI] FAILED to commit new user for {address}: {e_commit}", exc_info=True)
                    session.rollback()
                    return False


            sio.server.save_session(sid, {'user_id': user.id, 'user_address': user.public_address, 'user_signature': signature}, namespace='/gui-socket')
            join_room(str(user.id), sid, namespace='/gui-socket')

            join_room('broadcast', sid, namespace='/gui-socket')

            app.logger.info(f"[Gateway GUI] Auth success for {address} (User ID: {user.id}). SID {sid} joined room '{user.id}'.")

            owned = session.query(RegisteredEngine).filter_by(user_id=user.id).all()
            shared = session.query(EngineShare).filter_by(user_id=user.id).options(joinedload(EngineShare.engine)).all()

            all_engines = list(owned)
            if shared:
                for s in shared:
                    if s.engine:
                        all_engines.append(s.engine)

            statuses = []
            for eng in all_engines:
                if not eng: continue

                live_sid = globals_instance.engine_manager.active_engine_sessions.get(str(eng.id))
                status = 'offline'
                if live_sid:
                    status = 'online'

                statuses.append({
                    'engine_id': eng.id,
                    'status': status,
                    'vitals': None
                })

            sio.emit('initial_engine_statuses', statuses, room=sid, namespace='/gui-socket')
            return True

        except Exception as e:
            app.logger.error(f"[Gateway GUI] DB error during auth/setup: {e}", exc_info=True)
            session.rollback()
            return False
        finally:
            session.close()

    @sio.on('disconnect', namespace='/gui-socket')
    def on_gui_disconnect():
        app = current_app._get_current_object()
        sid = request.sid
        sess = _safe_get_session(sid, namespace='/gui-socket')
        if sess is None:
            app.logger.warning(f"[Gateway GUI Disconnect] GUI SID {sid} disconnected with no session.")
            return
        user_id = sess.get('user_id')
        app.logger.info(f"[Gateway GUI Disconnect] GUI for User {user_id} disconnected. SID: {sid}")
        try:
            if user_id:
                leave_room(str(user_id), sid, namespace='/gui-socket')
            gui_session_id = sess.get('gui_session_id')
            if gui_session_id:
                leave_room(gui_session_id, sid, namespace='/gui-socket')
                app.logger.info(f"[Gateway GUI Disconnect] SID {sid} left agent session room '{gui_session_id}'.")
        except Exception:
            pass