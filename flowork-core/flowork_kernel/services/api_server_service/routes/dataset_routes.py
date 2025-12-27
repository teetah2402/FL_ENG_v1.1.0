########################################################################
# WEBSITE https://flowork.cloud
# File NAME : C:\flowork-nano\flowork-core\flowork_kernel\services\api_server_service\routes\dataset_routes.py total lines 53 
########################################################################

from .base_api_route import BaseApiRoute

class DatasetRoutes(BaseApiRoute):

    def register_routes(self):
        return {
            "GET /api/v1/datasets": self.handle_get_datasets,
            "POST /api/v1/datasets": self.handle_post_datasets,
            "DELETE /api/v1/datasets/{dataset_name}": self.handle_delete_dataset,
            "GET /api/v1/datasets/{dataset_name}/data": self.handle_get_dataset_data,
            "POST /api/v1/datasets/{dataset_name}/data": self.handle_post_dataset_data,
            "PUT /api/v1/datasets/{dataset_name}/data": self.handle_put_dataset_row,
            "DELETE /api/v1/datasets/{dataset_name}/data/{row_id}": self.handle_delete_dataset_row,
        }

    async def handle_get_datasets(self, request):

        return self._json_response([])

    async def handle_post_datasets(self, request):
        return self._json_response(
            {"error": "Dataset creation is disabled in Open Core."}, status=501
        )

    async def handle_get_dataset_data(self, request):

        return self._json_response([])

    async def handle_post_dataset_data(self, request):
        return self._json_response(
            {"error": "Dataset modification is disabled in Open Core."}, status=501
        )

    async def handle_delete_dataset(self, request):
        return self._json_response(
            {"error": "Dataset deletion is disabled in Open Core."}, status=501
        )

    async def handle_put_dataset_row(self, request):
        return self._json_response(
            {"error": "Dataset modification is disabled in Open Core."}, status=501
        )

    async def handle_delete_dataset_row(self, request):
        return self._json_response(
            {"error": "Dataset modification is disabled in Open Core."}, status=501
        )
