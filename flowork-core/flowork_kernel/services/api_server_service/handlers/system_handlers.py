########################################################################
# WEBSITE https://flowork.cloud
# File NAME : C:\flowork-nano\flowork-core\flowork_kernel\services\api_server_service\handlers\system_handlers.py total lines 30 
########################################################################

from aiohttp import web
import asyncio
import logging


class SystemHandlersMixin:
    async def handle_ops_advice(self, request):
        """
        [LITE MODE STUB]
        OpsService has been removed to reduce footprint.
        This endpoint returns a static response to keep the API contract valid.
        """
        try:
            advice_data = {
                "status": "active",
                "mode": "lite_edge",
                "message": "Autoscaling advice service is disabled in Flowork Lite.",
                "actions": []
            }
            return web.json_response(advice_data, status=200)

        except Exception as e:
            logging.error(f"[OpsAdvice] Stub error: {e}", exc_info=True)
            return web.json_response({"error": "Internal Server Error", "message": str(e)}, status=500)
