########################################################################
# WEBSITE https://flowork.cloud
# File NAME : C:\flowork-nano\flowork-core\flowork_kernel\services\gateway_connector_service\handlers\ai_handler.py total lines 147 
########################################################################

import asyncio
from flowork_kernel.fac_enforcer import FacRuntime
from flowork_kernel.exceptions import PermissionDeniedError
from .base_handler import BaseHandler, CURRENT_PAYLOAD_VERSION

class AIHandler(BaseHandler):
    def register_events(self):
        @self.sio.event(namespace='/engine-socket')
        async def gw_start_session(data):
            session_id = data.get('session_id')
            engine_id = data.get('engine_id')
            fac_dict = data.get('fac')
            self.logger.info(f"[Core] Received 'gw:start_session' from Gateway for session: {session_id}")

            try:
                self.logger.warning(f"[Core] Session {session_id} rejected. AgentExecutorService is disabled in Open Core.")
                await self.service.emit_to_gateway('core:agent_error', {
                    'session_id': session_id,
                    'code': 'FEATURE_DISABLED',
                    'message': 'Autonomous Agents are disabled in Flowork Web3 Open Core Edition.'
                })
                return # Stop execution here
            except Exception as e:
                self.logger.error(f"[Core] Failed to send disabled signal: {e}")


        @self.sio.event(namespace='/engine-socket')
        async def gw_cancel_session(data):
            session_id = data.get('session_id')
            self.logger.info(f"[Core] Received 'gw:cancel_session' from Gateway for session: {session_id}")

            if session_id in self.service.g_active_sessions:
                del self.service.g_active_sessions[session_id]
                self.logger.info(f"[Core] Removed active FAC runtime for cancelled session {session_id}.")


        @self.sio.event(namespace='/engine-socket')
        async def gw_agent_input(data):
            session_id = data.get('session_id')
            self.logger.info(f"[Core] Received 'gw:agent_input' from Gateway for session: {session_id}")

            await self.service.emit_to_gateway('core:agent_error', {
                'session_id': session_id,
                'code': 'FEATURE_DISABLED',
                'message': 'Agent chat is disabled in Flowork Web3 Open Core Edition.'
            })
            return


        @self.sio.event(namespace='/engine-socket')
        async def gateway_execute_swarm_task(data):
            task_payload = data.get('task_payload', {})
            task_id = task_payload.get('task_id')

            if not task_id:
                self.logger.error(f"[Gateway R6] Received 'gateway_execute_swarm_task' with no task_id. Ignoring.")
                return

            self.logger.info(f"[Gateway R6] Received task {task_id} from Gateway. SWARM DISABLED.")

            result = {"error": "EngineError: Swarm/Agent features are disabled in Open Core."}


            self.logger.info(f"[Gateway R6] Execution for {task_id} complete. Sending result back to Gateway.")

            await self.service.emit_to_gateway('core:swarm_task_result', {
                "task_id": task_id,
                "result": result
            })

        @self.sio.event(namespace='/engine-socket')
        async def gateway_swarm_task_result(data):
            task_id = data.get('task_id')
            result = data.get('result', {})

            if not task_id:
                self.logger.error(f"[Gateway R6] Received 'gateway_swarm_task_result' with no task_id. Dropping.")
                return

            self.logger.info(f"[Gateway R6] Received result for *our* pending task: {task_id}")

            async with self.service._pending_swarm_tasks_lock:
                task_future = self.service._pending_swarm_tasks.get(task_id)

            if task_future and not task_future.done():
                task_future.set_result(result)
            else:
                self.logger.warning(f"[Gateway R6] Received result for unknown or already-timed-out task {task_id}. Ignoring.")

        @self.sio.event(namespace='/engine-socket')
        async def request_local_models(data):
            if not isinstance(data, dict) or data.get('v') != CURRENT_PAYLOAD_VERSION: return
            real_data = data.get('payload', {})
            user_id = real_data.get('user_context', {}).get('id')
            self.logger.info(f"Received 'request_local_models' from user {user_id}")
            models_list = []
            error_msg = None
            try:
                ai_manager = self.service.kernel_services.get("ai_provider_manager_service")
                if ai_manager:
                    models_list = [
                        {"id": model_id, "name": model_data.get("name", model_id)}
                        for model_id, model_data in ai_manager.local_models.items()
                        if model_data.get("category") == "text"
                    ]
                else:
                    error_msg = "AIProviderManagerService not found."
            except Exception as e:
                error_msg = str(e)
            versioned_response = {'v': CURRENT_PAYLOAD_VERSION, 'payload': {'models': models_list, 'error': error_msg, '_target_user_id': user_id}}
            await self.sio.emit('response_local_models', versioned_response, namespace='/engine-socket')

        @self.sio.event(namespace='/engine-socket')
        async def start_training_job(data):
            if not isinstance(data, dict) or data.get('v') != CURRENT_PAYLOAD_VERSION: return
            real_data = data.get('payload', {})
            user_id = real_data.get('user_context', {}).get('id')
            config = real_data.get('config')
            self.logger.info(f"Received 'start_training_job' from user {user_id} for {config.get('new_model_name')}")

            error_msg = "Fine-tuning disabled in Open Core."
            versioned_response = {'v': CURRENT_PAYLOAD_VERSION, 'payload': {'jobs': [], 'error': error_msg, '_target_user_id': user_id}}
            await self.sio.emit('response_training_job_status', versioned_response, namespace='/engine-socket')


        @self.sio.event(namespace='/engine-socket')
        async def request_training_job_status(data):
            if not isinstance(data, dict) or data.get('v') != CURRENT_PAYLOAD_VERSION: return
            real_data = data.get('payload', {})
            user_id = real_data.get('user_context', {}).get('id')
            await self._send_training_status(user_id)

        async def _send_training_status(self, user_id):
            """ Helper to avoid code duplication since it is called from two places """
            self.logger.info(f"Received 'request_training_job_status' from user {user_id}")
            jobs_list = []
            error_msg = "Training disabled in Open Core."


            versioned_response = {'v': CURRENT_PAYLOAD_VERSION, 'payload': {'jobs': jobs_list, 'error': error_msg, '_target_user_id': user_id}}
            await self.sio.emit('response_training_job_status', versioned_response, namespace='/engine-socket')
