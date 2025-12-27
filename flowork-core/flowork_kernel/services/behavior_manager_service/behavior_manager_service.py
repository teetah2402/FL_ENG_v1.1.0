########################################################################
# WEBSITE https://flowork.cloud
# File NAME : C:\flowork-nano\flowork-core\flowork_kernel\services\behavior_manager_service\behavior_manager_service.py total lines 20 
########################################################################

from ..base_service import BaseService
from .behavior_handlers import RetryHandler, LoopHandler
class BehaviorManagerService(BaseService):

    def __init__(self, kernel, service_id: str):
        super().__init__(kernel, service_id)
        self.registered_behaviors = {
            "retry": RetryHandler,
            "loop": LoopHandler
        }
        self.kernel.write_to_log("Service 'BehaviorManager' initialized successfully.", "DEBUG")
    def wrap_execution(self, module_id, original_execute_func):

        return original_execute_func
