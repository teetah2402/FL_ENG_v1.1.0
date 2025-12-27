########################################################################
# WEBSITE https://flowork.cloud
# File NAME : C:\flowork-nano\flowork-core\flowork_kernel\services\api_server_service\middleware.py total lines 173 
########################################################################

import time
import os
import re
import secrets
from aiohttp import web
from flowork_kernel.utils.tracing_setup import get_trace_context_from_headers

DEFAULT_SECRET = "flowork_default_secret_2025"

class MiddlewareMixin:
    def log_recent_event(self, event_string: str):
        if "dashboard/summary" in event_string or "/health" in event_string:
            return
        timestamp = time.strftime("%H:%M:%S")
        self.recent_events.appendleft(f"[{timestamp}] {event_string}")

    def _authenticate_request(self, request):
        if hasattr(self.kernel, 'is_dev_mode') and self.kernel.is_dev_mode:
            return True

        expected_key = os.getenv("GATEWAY_SECRET_TOKEN", DEFAULT_SECRET)

        if not expected_key:
            self.kernel.write_to_log(
                "GATEWAY_SECRET_TOKEN not set and no DEFAULT. Skipping internal API authentication check.", "WARN"
            )
            return True
        provided_key = request.headers.get("X-API-Key")
        if provided_key and secrets.compare_digest(provided_key, expected_key):
            return True

        provided_key_snippet = f"'{provided_key[:5]}...'" if provided_key else "'None'"
        expected_key_snippet = f"'{expected_key[:5]}...'" if expected_key else "'None (Not Set)'"
        self.kernel.write_to_log(
            f"Unauthorized API access attempt to {request.path}. Provided key: {provided_key_snippet} (Expected starts with {expected_key_snippet})", "CRITICAL"
        )
        return False

    async def middleware_handler(self, arg1, arg2):
        if isinstance(arg1, web.Request):
            return await self._run_middleware_logic(arg1, arg2)
        else:
            async def middleware_wrapper(request):
                return await self._run_middleware_logic(request, arg2)
            return middleware_wrapper

    async def _run_middleware_logic(self, request, handler):
        start_time = time.time()

        client_ip = "0.0.0.0"
        if hasattr(request, 'remote') and request.remote:
            client_ip = request.remote

        trace_context = get_trace_context_from_headers(request.headers)
        span_name = f"{request.method} {request.path}"

        with self.tracer.start_as_current_span(span_name, context=trace_context) as span:
            span.set_attribute("http.method", request.method)
            span.set_attribute("http.url", str(request.url))
            span.set_attribute("net.peer.ip", client_ip)

            origin = request.headers.get("Origin")
            trusted_guis = {
                "https://flowork.cloud",
                "https://momod.flowork.cloud",
                "https://api.flowork.cloud",
                "https://flowork.pages.dev",
                "http://localhost:5173",
                "http://localhost:4173",
                "http://localhost:8002",
                "http://localhost:5001"
            }

            env_socket_url = os.getenv("SOCKET_URL")
            if env_socket_url:
                trusted_guis.add(env_socket_url)

            cors_origin = ""
            if origin in trusted_guis:
                cors_origin = origin

            headers = {
                "Access-Control-Allow-Origin": cors_origin,
                "Access-Control-Allow-Credentials": "true",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, PATCH, OPTIONS",
                "Access-Control-Allow-Headers": "X-API-Key, Content-Type, Authorization, X-Flowork-User-ID, X-Flowork-Engine-ID, X-Signature, X-User-Address, X-Signed-Message, traceparent, x-gateway-token, ngrok-skip-browser-warning",
            }

            if request.method == "OPTIONS":
                return web.Response(status=204, headers=headers)

            self.log_recent_event(f"[{request.method}] {request.path}")

            public_routes_patterns = [
                r"^/health$",
                r"^/metrics$",
                r"^/webhook/.*$",
                r"^/api/v1/status$",
                r"^/api/v1/localization/.*$",
                r"^/api/v1/(modules|plugins|tools|apps|triggers|ai_providers|components)/.*$",
                r"^/api/v1/presets/.*$",
                r"^/api/v1/dashboard/.*$",
                r"^/api/v1/news$",
                r"^/api/v1/datasets.*$",
                r"^/api/v1/models/.*$",
                r"^/api/v1/ai/.*$",
                r"^/api/v1/training/.*$",
                r"^/api/v1/neural-ingestor/.*$",
                r"^/ops/advice$"
            ]

            is_public_route = any(re.match(pattern, request.path) for pattern in public_routes_patterns)

            if not is_public_route and not self._authenticate_request(request):
                span.set_attribute("http.status_code", 401)
                span.set_attribute("flowork.error_reason", "Invalid API Key")
                return web.json_response(
                    {"error": "Unauthorized: API Key is missing or invalid."}, status=401, headers=headers
                )

            request["user_context"] = {
                "user_id": request.headers.get("X-Flowork-User-ID"),
                "engine_id": request.headers.get("X-Flowork-Engine-ID"),
            }

            span.set_attribute("flowork.user_id", request["user_context"]["user_id"])
            span.set_attribute("flowork.engine_id", request["user_context"]["engine_id"])

            try:
                response = await handler(request)

                if not isinstance(response, web.StreamResponse):
                    if isinstance(response, dict):
                        response = web.json_response(response)
                    elif response is None:
                        response = web.json_response({})

                if hasattr(response, 'prepared') and not response.prepared:
                    for key, value in headers.items():
                        response.headers[key] = value

                if response:
                    span.set_attribute("http.status_code", response.status)

                return response

            except web.HTTPException as http_exc:
                span.set_attribute("http.status_code", http_exc.status_code)
                span.set_attribute("flowork.error_reason", f"HTTPException: {http_exc.reason}")
                if not http_exc.prepared:
                    http_exc.headers.update(headers)
                raise http_exc

            except Exception as e:
                self.kernel.write_to_log(f"Unhandled error in API handler for {request.path}: {e}", "CRITICAL")
                import traceback
                self.kernel.write_to_log(traceback.format_exc(), "DEBUG")

                span.set_attribute("http.status_code", 500)
                span.set_attribute("flowork.error_reason", f"Unhandled Exception: {type(e).__name__}")
                span.record_exception(e)

                return web.json_response(
                    {"error": "Internal Server Error", "details": str(e)}, status=500, headers=headers
                )
            finally:
                pass
