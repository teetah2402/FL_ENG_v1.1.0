########################################################################
# WEBSITE https://flowork.cloud
# File NAME : C:\flowork-nano\flowork-core\flowork_kernel\services\api_server_service\routes\app_routes.py total lines 53 
########################################################################

from flask import Blueprint, request, jsonify
from flowork_kernel.globals import globals_instance

app_router_bp = Blueprint('app_router_bp', __name__)

@app_router_bp.route('/execute/<app_id>/<action>', methods=['POST'])
def execute_app_action(app_id, action):
    """
    Endpoint Sakti: Menerima request POST dan menembak App yang sesuai.
    Contoh: POST /api/v1/apps/execute/test_factory/hello
    Body: {"name": "Boss Besar"}
    """
    try:
        lifecycle_svc = globals_instance.get_service("app_lifecycle_service")

        if not lifecycle_svc:
            return jsonify({"error": "App Factory Service not running"}), 503

        app_service = lifecycle_svc.loaded_apps.get(app_id)

        if not app_service:
            return jsonify({"error": f"App '{app_id}' not found or offline"}), 404

        if not hasattr(app_service, 'router'):
             try:
                 from importlib import import_module
                 module = import_module(f"apps.{app_id}.backend.router")
                 app_service.router = module.AppRouter(app_service)
             except ImportError:
                 return jsonify({"error": f"App '{app_id}' has no router.py"}), 501
             except Exception as e:
                 return jsonify({"error": f"Router Init Failed: {e}"}), 500

        routes = app_service.router.get_routes()

        if action not in routes:
            return jsonify({"error": f"Action '{action}' not found in App '{app_id}'"}), 400

        payload = request.json or {}
        handler_func = routes[action]

        result = handler_func(payload)

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": "App Execution Failed", "details": str(e)}), 500
