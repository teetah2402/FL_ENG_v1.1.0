from flask import request, current_app
from app.globals import globals_instance
from .utils import _safe_get_session, g_swarm_task_registry

def register_handlers(sio):

    @sio.on('core:request_swarm_task', namespace='/engine-socket')
    def on_core_request_swarm_task(data):
        app = current_app._get_current_object()
        origin_sid = request.sid
        origin_sess = _safe_get_session(origin_sid, namespace='/engine-socket')
        if not origin_sess:
            app.logger.warning(f"[Gateway R6] Swarm task request from unauthed SID {origin_sid}. Dropping.")
            return

        origin_user_id = origin_sess.get('user_id')
        target_engine_id = data.get('target_engine_id')
        task_payload = data.get('task_payload', {})
        task_id = task_payload.get('task_id')

        if not all([origin_user_id, target_engine_id, task_id]):
            app.logger.error(f"[Gateway R6] Invalid swarm task request from {origin_sess.get('engine_id')}. Missing fields.")
            sio.emit('gateway:swarm_task_result', {
                "task_id": task_id or "unknown",
                "result": {"error": "GatewayError: Invalid swarm request. Missing target_engine_id or task_id."}
            }, room=origin_sid, namespace='/engine-socket')
            return

        app.logger.info(f"[Gateway R6] Request from SID {origin_sid} for task {task_id} -> Target Engine {target_engine_id}")

        target_sid = globals_instance.engine_manager.active_engine_sessions.get(target_engine_id)
        if not target_sid:
            app.logger.warning(f"[Gateway R6] Target engine {target_engine_id} is OFFLINE. Failing task {task_id}.")
            sio.emit('gateway:swarm_task_result', {
                "task_id": task_id,
                "result": {"error": f"GatewayError: Target engine '{target_engine_id}' is offline."}
            }, room=origin_sid, namespace='/engine-socket')
            return

        target_sess = _safe_get_session(target_sid, namespace='/engine-socket')
        if not target_sess or target_sess.get('user_id') != origin_user_id:
            app.logger.error(f"[Gateway R6] AuthZ FAIL: Engine {origin_sess.get('engine_id')} (User {origin_user_id}) " \
                             f"tried to swarm task to {target_engine_id} (User {target_sess.get('user_id')}).")
            sio.emit('gateway:swarm_task_result', {
                "task_id": task_id,
                "result": {"error": f"GatewayError: Permission denied to access engine '{target_engine_id}'."}
            }, room=origin_sid, namespace='/engine-socket')
            return

        g_swarm_task_registry[task_id] = origin_sid
        app.logger.info(f"[Gateway R6] Task {task_id} registered. Origin SID {origin_sid} is waiting.")

        sio.emit(
            'gateway:execute_swarm_task',
            {"task_payload": task_payload},
            room=target_sid,
            namespace='/engine-socket'
        )
        app.logger.info(f"[Gateway R6] Task {task_id} forwarded to Target SID {target_sid} (Engine {target_engine_id}).")

    @sio.on('core:swarm_task_result', namespace='/engine-socket')
    def on_core_swarm_task_result(data):
        app = current_app._get_current_object()
        worker_sid = request.sid
        worker_sess = _safe_get_session(worker_sid, namespace='/engine-socket')

        task_id = data.get('task_id')
        result = data.get('result', {})

        if not task_id:
            app.logger.error(f"[Gateway R6] Received swarm result from {worker_sess.get('engine_id')} with no task_id. Dropping.")
            return

        app.logger.info(f"[Gateway R6] Received result for task {task_id} from worker {worker_sess.get('engine_id')}.")

        origin_sid = g_swarm_task_registry.pop(task_id, None)
        if not origin_sid:
            app.logger.warning(f"[Gateway R6] Cannot route result for task {task_id}. Origin SID not found in registry (maybe timed out or duplicate?). Dropping.")
            return

        sio.emit(
            'gateway:swarm_task_result',
            {
                "task_id": task_id,
                "result": result
            },
            room=origin_sid,
            namespace='/engine-socket'
        )
        app.logger.info(f"[Gateway R6] Result for {task_id} forwarded back to Origin SID {origin_sid}.")