########################################################################
# WEBSITE https://flowork.cloud
# File NAME : C:\FLOWORK\flowork-gateway\app\routes\apps.py total lines 221 
########################################################################

import requests
import os
from flask import Blueprint, request, jsonify, g, current_app, Response, make_response
from functools import wraps
from ..helpers import crypto_auth_required, get_db_session
from ..globals import globals_instance
from ..models import RegisteredEngine

apps_bp = Blueprint('apps', __name__)

DEFAULT_SECRET = "flowork_default_secret_2025"

def handle_cors_options(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method == 'OPTIONS':
            response = make_response()
            response.headers.add("Access-Control-Allow-Origin", request.headers.get('Origin', '*'))
            response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization, X-API-Key, X-Flowork-User-ID, X-Flowork-Engine-ID, X-Gateway-Secret, x-signed-message, x-signature, x-user-address, x-payload-version")
            response.headers.add("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, PATCH, OPTIONS")
            response.headers.add("Access-Control-Allow-Credentials", "true")

            response.headers.add("Access-Control-Allow-Private-Network", "true")

            return response
        return f(*args, **kwargs)
    return decorated_function

def _resolve_target_engine_url(target_engine_id):
    """Mencari alamat internal mesin tanpa menyebabkan crash"""
    engine_manager = globals_instance.engine_manager
    if target_engine_id in engine_manager.engine_url_map:
        return engine_manager.engine_url_map[target_engine_id], None

    session = get_db_session()
    try:
        engine = session.query(RegisteredEngine).filter_by(id=target_engine_id).first()
        if engine:
            return "http://flowork_core:8989", None

        if target_engine_id in ['local', 'default', 'self']:
             return "http://flowork_core:8989", None

        return None, f"Engine {target_engine_id} not found"
    except Exception as e:
        return None, str(e)
    finally:
        session.close()

def get_engine_id_from_request():
    """Mata-mata penangkap ID dari Header atau Query Param"""
    eid = request.headers.get("X-Flowork-Engine-ID") or request.args.get("engine_id")
    if not eid:
        return "local"
    return str(eid).strip()

@apps_bp.route('', methods=['GET', 'OPTIONS'])
@handle_cors_options
def list_apps():
    target_engine_id = get_engine_id_from_request()

    core_url, error = _resolve_target_engine_url(target_engine_id)
    if error:
        print(f"[Apps] Engine Resolution Failed: {error}")
        return jsonify([]), 200

    try:
        target_endpoint = f"{core_url}/api/v1/apps"
        api_key = os.getenv("GATEWAY_SECRET_TOKEN", DEFAULT_SECRET)

        headers = {
            "X-API-Key": api_key,
            "X-Flowork-User-ID": str(g.user.id) if hasattr(g, 'user') else "system"
        }

        resp = requests.get(target_endpoint, headers=headers, timeout=5)

        return Response(
            resp.content,
            status=resp.status_code,
            content_type=resp.headers.get('Content-Type', 'application/json')
        )
    except Exception as e:
        print(f"[Apps] Fetch Error: {e}")
        return jsonify([]), 200

@apps_bp.route('/nodes', methods=['GET', 'OPTIONS'])
@handle_cors_options
def list_app_nodes():
    target_engine_id = get_engine_id_from_request()
    core_url, error = _resolve_target_engine_url(target_engine_id)

    if error: return jsonify({"error": error}), 502

    try:
        target_endpoint = f"{core_url}/api/v1/apps/nodes"
        api_key = os.getenv("GATEWAY_SECRET_TOKEN", DEFAULT_SECRET)

        headers = {
            "X-API-Key": api_key,
            "X-Flowork-User-ID": str(g.user.id) if hasattr(g, 'user') else "system"
        }

        resp = requests.get(target_endpoint, headers=headers, timeout=5)

        return Response(
            resp.content,
            status=resp.status_code,
            content_type=resp.headers.get('Content-Type', 'application/json')
        )
    except Exception as e:
        return jsonify({"error": "Fetch Nodes Failed", "details": str(e)}), 500

@apps_bp.route('/<app_id>/actions', methods=['GET', 'OPTIONS'])
@handle_cors_options
def list_app_actions(app_id):
    target_engine_id = get_engine_id_from_request()
    core_url, error = _resolve_target_engine_url(target_engine_id)

    if error: return jsonify({"error": error}), 502

    try:
        target_endpoint = f"{core_url}/api/v1/apps/{app_id}/actions"
        api_key = os.getenv("GATEWAY_SECRET_TOKEN", DEFAULT_SECRET)

        headers = {
            "X-API-Key": api_key,
            "X-Flowork-User-ID": str(g.user.id) if hasattr(g, 'user') else "system"
        }

        resp = requests.get(target_endpoint, headers=headers, timeout=5)

        return Response(
            resp.content,
            status=resp.status_code,
            content_type=resp.headers.get('Content-Type', 'application/json')
        )
    except Exception as e:
        return jsonify({"error": "Fetch Actions Failed", "details": str(e)}), 500

@apps_bp.route('/<app_id>/icon', methods=['GET', 'OPTIONS'])
@handle_cors_options
def get_app_icon(app_id):
    target_engine_id = get_engine_id_from_request()
    core_url, error = _resolve_target_engine_url(target_engine_id)

    if error: return "Icon Not Found", 404

    try:
        target_url = f"{core_url}/api/v1/apps/{app_id}/assets/icon.svg"
        api_key = os.getenv("GATEWAY_SECRET_TOKEN", DEFAULT_SECRET)
        resp = requests.get(target_url, headers={"X-API-Key": api_key}, timeout=5)
        return Response(resp.content, content_type='image/svg+xml')
    except Exception:
        return Response('<svg></svg>', content_type='image/svg+xml')

@apps_bp.route('/<app_id>/assets/<path:filename>', methods=['GET', 'OPTIONS'])
@handle_cors_options
def get_app_asset(app_id, filename):
    target_engine_id = get_engine_id_from_request()
    core_url, error = _resolve_target_engine_url(target_engine_id)

    if error: return f"Routing Error: {error}", 502

    try:
        target_url = f"{core_url}/api/v1/apps/{app_id}/assets/{filename}"
        api_key = os.getenv("GATEWAY_SECRET_TOKEN", DEFAULT_SECRET)

        params = request.args

        resp = requests.get(target_url, headers={"X-API-Key": api_key}, params=params, stream=True, timeout=30)

        excluded_headers = ["content-encoding", "content-length", "transfer-encoding", "connection"]
        headers = [(n, v) for n, v in resp.raw.headers.items() if n.lower() not in excluded_headers]

        response = Response(resp.content, resp.status_code, headers)
        response.headers["Access-Control-Allow-Private-Network"] = "true"

        return response
    except Exception as e:
        return f"Tunnel Connection Failed: {str(e)}", 502

@apps_bp.route('/execute/<app_id>/<action>', methods=['POST', 'OPTIONS'])
@handle_cors_options
def execute_app_action(app_id, action):
    target_engine_id = get_engine_id_from_request()
    core_url, error = _resolve_target_engine_url(target_engine_id)

    if error: return jsonify({"error": f"Engine Error: {error}"}), 502

    try:
        target_url = f"{core_url}/api/v1/apps/execute/{app_id}/{action}"

        api_key = os.getenv("GATEWAY_SECRET_TOKEN", DEFAULT_SECRET)
        headers = {
            "X-API-Key": api_key,
            "Content-Type": "application/json",
            "X-Flowork-User-ID": str(g.user.id) if hasattr(g, 'user') else "system"
        }

        payload = request.json if request.is_json else {}

        resp = requests.post(target_url, json=payload, headers=headers, timeout=30)

        response = Response(
            resp.content,
            status=resp.status_code,
            content_type=resp.headers.get('Content-Type', 'application/json')
        )
        response.headers["Access-Control-Allow-Private-Network"] = "true"

        return response

    except Exception as e:
        return jsonify({"error": "Gateway Proxy Failed", "details": str(e)}), 500
