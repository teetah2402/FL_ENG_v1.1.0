########################################################################
# WEBSITE https://flowork.cloud
# File NAME : C:\flowork-nano\flowork-core\flowork_kernel\services\api_server_service\handlers\webhook_handlers.py total lines 36 
########################################################################

from aiohttp import web
import json

class WebhookHandlersMixin:
    async def handle_webhook_trigger(self, request):
        preset_name = request.match_info.get("preset_name")
        if not preset_name:
            return web.json_response({"error": "Preset name missing from URL."}, status=400)
        try:
            webhook_data = await request.json()
            self.kernel.write_to_log(f"Webhook received for preset '{preset_name}'. Triggering execution...", "INFO")
            user_context = request.get("user_context", None)
            job_id = await self.trigger_workflow_by_api(
                preset_name=preset_name,
                initial_payload=webhook_data,
                user_context=user_context,
                mode="EXECUTE"
            )
            if job_id:
                return web.json_response(
                    {"status": "success", "message": f"Workflow for preset '{preset_name}' was triggered.", "job_id": job_id},
                    status=202
                )
            else:
                return web.json_response({"error": "Failed to trigger workflow (e.g., preset not found)."}, status=404)
        except json.JSONDecodeError:
            return web.json_response({"error": "Bad Request: Body must be in valid JSON format."}, status=400)
        except Exception as e:
            self.kernel.write_to_log(f"Error handling webhook for preset '{preset_name}': {e}", "ERROR")
            return web.json_response({"error": f"Internal Server Error: {e}"}, status=500)
