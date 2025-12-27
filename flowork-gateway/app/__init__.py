########################################################################
# WEBSITE https://flowork.cloud
# File NAME : C:\FLOWORK\flowork-gateway\app\__init__.py total lines 195 
########################################################################

import logging
import os
import sys
from flask import Flask, jsonify, request, make_response
from flask_cors import CORS

from app.security.env_guard import guard_runtime, check_strict_env
from app.security.logging_setup import configure_logging

try:
    from .config import Config
except ImportError:
    try:
        from config import Config
    except ImportError:
        print("[FATAL] Could not load Config class. Check app/config.py")
        sys.exit(1)

from .extensions import db, migrate, socketio
from .extensions import db as gateway_db
from .metrics import register_metrics
from .rl.limiter import RateLimiter
from .db.router import db_router
from .ops.drain import drain_bp, init_drain_state
from .db.pragma import init_pragma
from app.etl.exporter import start_exporter_thread
from .ops.health import bp as health_bp

limiter = RateLimiter()

def create_app(config_class=Config):
    configure_logging()

    root_logger = logging.getLogger(__name__)

    app = Flask(__name__)
    app.config.from_object(config_class)

    @app.before_request
    def handle_preflight():
        if request.method == "OPTIONS":
            response = make_response()
            response.headers.add("Access-Control-Allow-Origin", request.headers.get('Origin', '*'))
            response.headers.add("Access-Control-Allow-Headers", "*")
            response.headers.add("Access-Control-Allow-Methods", "*")
            response.headers.add("Access-Control-Allow-Credentials", "true")
            response.headers.add("Access-Control-Allow-Private-Network", "true")
            return response

    @app.after_request
    def add_pna_header(response):
        origin = request.headers.get('Origin')
        if origin:
            response.headers['Access-Control-Allow-Origin'] = origin

        response.headers["Access-Control-Allow-Private-Network"] = "true"
        response.headers["Access-Control-Allow-Credentials"] = "true"
        return response

    if not app.config.get("SQLALCHEMY_DATABASE_URI"):
        fallback_db = f"sqlite:////app/data/gateway.db"
        app.config["SQLALCHEMY_DATABASE_URI"] = fallback_db

    app.logger = root_logger
    app.logger.info("[Startup] Initializing core services...")

    allowed_origins = [
        "https://flowork.cloud",
        "https://api.flowork.cloud",
        "https://flowork.pages.dev",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8990",
        "http://127.0.0.1:8990"
    ]

    CORS(app, origins=allowed_origins, supports_credentials=True)

    gateway_db.init_app(app)
    migrate.init_app(app, gateway_db)

    with app.app_context():
        try:
            init_pragma(app, gateway_db)
        except Exception as e:
            app.logger.error(f"[Startup] PRAGMA init failed: {e}")

    register_metrics(app)
    limiter.init_app(app)
    db_router.init_app(app)
    init_drain_state(app)

    socketio.init_app(
        app,
        async_mode='gevent',
        cors_allowed_origins="*",
        path='/api/socket.io'
    )

    from . import sockets
    from .routes.auth import auth_bp
    from .routes.system import system_bp
    from .routes.cluster import cluster_bp
    from .routes.dispatch import dispatch_bp
    from .ops.chaos import chaos_bp
    from .engine.heartbeat_api import engine_hb_bp
    from .routes.proxy import proxy_bp
    from .routes.user import user_bp
    from .routes.user_state import user_state_bp
    from .routes.presets import presets_bp
    from .routes.workflow_shares import workflow_shares_bp
    from .routes.dashboard import dashboard_bp
    from .routes.agent import agent_bp
    from .routes.capsules import bp as capsules_bp
    from .routes.marketplace import marketplace_bp
    from .routes.ai_proxy import ai_proxy_bp
    from .routes.apps import apps_bp

    from .routes.variables import variables_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(system_bp)
    app.register_blueprint(cluster_bp)
    app.register_blueprint(dispatch_bp)
    app.register_blueprint(chaos_bp)
    app.register_blueprint(drain_bp)
    app.register_blueprint(health_bp)
    app.register_blueprint(engine_hb_bp)
    app.register_blueprint(proxy_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(user_state_bp)
    app.register_blueprint(presets_bp)
    app.register_blueprint(workflow_shares_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(agent_bp)
    app.register_blueprint(capsules_bp)
    app.register_blueprint(marketplace_bp, url_prefix='/api/v1/marketplace')
    app.register_blueprint(ai_proxy_bp, url_prefix='/api/v1/ai')
    app.register_blueprint(apps_bp, url_prefix='/api/v1/apps')
    app.register_blueprint(variables_bp, url_prefix='/api/v1/variables')

    app.logger.info("[Startup] Flowork Gateway blueprints registered.")
    start_exporter_thread(app)

    @app.teardown_appcontext
    def remove_db_session(exception=None):
        gateway_db.session.remove()

    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({"error": "Not Found"}), 404

    @app.errorhandler(500)
    def internal_error(error):
        app.logger.exception("Internal server error")
        return jsonify({"error": "Internal Server Error"}), 500

    from app.rl.limiter import init_rl_schema, allow as rl_allow
    with app.app_context():
        try:
            init_rl_schema()
        except Exception:
             pass

    USER_RATE = float(os.getenv("USER_RATE", "5"))
    USER_BURST = float(os.getenv("USER_BURST", "20"))
    ENGINE_RATE = float(os.getenv("ENGINE_RATE", "20"))
    ENGINE_BURST = float(os.getenv("ENGINE_BURST", "100"))

    @app.before_request
    def _apply_rl():
        if request.method == "OPTIONS": return # Skip rate limit for preflight
        if request.path.startswith("/health") or request.path.startswith("/metrics"): return
        if "enqueue" in request.path:
            body = (request.get_json(silent=True) or {})
            if body:
                uid = body.get("user_id","anon")
                eid = body.get("engine_id","default")
                ok1, ra1 = rl_allow(f"user:{uid}", USER_RATE, USER_BURST)
                ok2, ra1 = rl_allow(f"engine:{eid}", ENGINE_RATE, ENGINE_BURST)
                if not (ok1 and ok2):
                    retry_after = max(ra1, ra1, 1)
                    resp = jsonify({"error":"rate_limited","retry_after": retry_after})
                    resp.status_code = 429
                    resp.headers["Retry-After"] = str(retry_after)
                    return resp

    app.logger.info("[Startup] Flowork Gateway initialized.")
    return app
