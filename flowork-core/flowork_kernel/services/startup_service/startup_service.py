########################################################################
# WEBSITE https://flowork.cloud
# File NAME : C:\FLOWORK\flowork-core\flowork_kernel\services\startup_service\startup_service.py
########################################################################

from flowork_kernel.services.base_service import BaseService
import logging

class StartupService(BaseService):
    # PERBAIKAN: Tambahkan service_id agar sesuai dengan panggilan Orchestrator (3 argumen)
    # Kode Lama: def __init__(self, kernel):
    def __init__(self, kernel, service_id: str):
        if not hasattr(self, 'logger'):
            self.logger = logging.getLogger('Node.startup_service')

        # Panggil super dengan service_id
        super().__init__(kernel, service_id)
        self.logger.info("StartupService initialized successfully.")

    def run(self, *args, **kwargs):
        """Logic eksekusi saat startup dimulai"""
        self.logger.info("🚀 Orchestrating initial system sequence...")
        return {"status": "success", "message": "System startup sequence complete"}