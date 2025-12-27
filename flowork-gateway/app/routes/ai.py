########################################################################
# WEBSITE https://flowork.cloud
# File NAME : C:\flowork-nano\flowork-gateway\app\routes\ai.py total lines 89 
########################################################################

import os
import logging
import requests
from flask import Blueprint, request, jsonify, Response, stream_with_context, make_response

ai_bp = Blueprint('ai_bp', __name__)
prompts_bp = Blueprint('prompts_bp', __name__)

logger = logging.getLogger(__name__)
CORE_INTERNAL_URL = os.getenv("FLOWORK_CORE_INTERNAL_URL", "http://flowork_core:8989")

def get_crypto_auth():
    try:
        from app.helpers import crypto_auth_required
        return crypto_auth_required
    except ImportError:
        return lambda x: x

def _add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = request.headers.get('Origin', '*')
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    response.headers['Access-Control-Allow-Headers'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS, PUT, DELETE, PATCH'
    return response

@prompts_bp.route('/', methods=['GET', 'POST', 'OPTIONS'])
def handle_prompts():
    if request.method == 'OPTIONS': return _add_cors_headers(make_response())

    try:
        target_url = f"{CORE_INTERNAL_URL}/api/v1/prompts"

        excluded = ['host', 'content-length', 'content-type', 'connection']
        safe_headers = {k: v for k, v in request.headers.items() if k.lower() not in excluded}

        if request.method == 'GET':
            resp = requests.get(target_url, headers=safe_headers, params=request.args.to_dict(), timeout=5)
        else:
            resp = requests.post(target_url, headers=safe_headers, json=request.get_json(silent=True), timeout=10)

        return Response(resp.content, status=resp.status_code, content_type=resp.headers.get('Content-Type'))

    except Exception as e:
        logger.exception(f"💥 [PROXY] Prompts Error: {e}")
        return jsonify({"error": str(e)}), 500

@ai_bp.route('/<path:subpath>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'])
def ai_entry(subpath):
    if request.method == 'OPTIONS': return _add_cors_headers(make_response())

    auth = get_crypto_auth()
    @auth
    def handler(subpath):
        return _proxy_logic(subpath)
    return handler(subpath)

def _proxy_logic(subpath):
    target_url = f"{CORE_INTERNAL_URL}/api/v1/ai/{subpath}"

    excluded = ['host', 'content-length', 'connection', 'transfer-encoding']
    safe_headers = {k: v for k, v in request.headers.items() if k.lower() not in excluded}

    try:
        resp = requests.request(
            method=request.method,
            url=target_url,
            headers=safe_headers,
            data=request.get_data(),
            params=request.args.to_dict(),
            stream=True,
            timeout=600
        )

        def generate():
            for chunk in resp.iter_content(chunk_size=1024):
                if chunk: yield chunk

        headers_back = [(k,v) for k,v in resp.headers.items() if k.lower() not in ['content-encoding', 'transfer-encoding']]
        return _add_cors_headers(Response(stream_with_context(generate()), status=resp.status_code, headers=headers_back))

    except Exception as e:
        logger.error(f"💥 [AI Proxy] Error: {e}")
        return jsonify({"error": str(e)}), 500
