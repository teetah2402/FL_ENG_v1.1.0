########################################################################
# WEBSITE https://flowork.cloud
# File NAME : C:\flowork-nano\apps\flowork_architect\backend\router.py total lines 63 
########################################################################

from flowork_kernel.router import BaseRouter
from .service import ArchitectService

class AppRouter(BaseRouter):
    """
    NEURAL ARCHITECT ROUTER
    Maps frontend GUI actions to Backend Service logic.
    """
    def __init__(self, app_context):
        real_kernel = getattr(app_context, 'kernel', app_context)
        super().__init__(real_kernel)
        self.service = ArchitectService(real_kernel, "flowork_architect_service")

    def get_routes(self):
        """
        Mapping endpoint API.
        URL: /api/v1/apps/execute/flowork_architect/{route_name}
        """
        return {
            "scan": self.run_scan,          # Load Graph
            "force_sync": self.force_sync,  # Re-index
            "get_intel": self.get_intel,    # File Details
            "export_atlas": self.export_atlas, # CSV Export
            "export_json": self.export_json,   # JSON Export (NEW)
            "save_file": self.save_file,    # Monaco Editor Save
            "crud": self.crud_action        # Create/Delete/Rename
        }

    async def run_scan(self, payload):
        return {
            "status": "success",
            "data": self.service.run_scan()
        }

    async def force_sync(self, payload):
        return self.service.force_sync()

    async def get_intel(self, payload):
        return self.service.get_file_intel(
            payload.get("path"),
            payload.get("all_nodes", [])
        )

    async def export_atlas(self, payload):
        return self.service.export_atlas()

    async def export_json(self, payload):
        return self.service.export_json_atlas()

    async def save_file(self, payload):
        return self.service.save_file(
            payload.get("path"),
            payload.get("content")
        )

    async def crud_action(self, payload):
        return self.service.handle_crud(payload)
