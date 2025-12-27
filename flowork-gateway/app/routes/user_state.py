########################################################################
# WEBSITE https://flowork.cloud
# File NAME : C:\FLOWORK\flowork-gateway\app\routes\user_state.py total lines 132 
########################################################################

from flask import Blueprint, jsonify, request, current_app, g
from ..extensions import db
from ..models import User, State
from ..helpers import crypto_auth_required

user_state_bp = Blueprint("user_state", __name__, url_prefix="/api/v1/user/state")

FAVORITE_PRESETS_KEY = "favorite_presets"
FAVORITE_COMPONENTS_KEY = "favorite_components"

ACTIVE_APPS_KEY = "active_apps"
ACTIVE_WIDGETS_KEY = "active_widgets"

@user_state_bp.route(f"/{FAVORITE_PRESETS_KEY}", methods=["GET"])
@crypto_auth_required
def get_favorite_presets():
    current_user = g.user
    try:
        state_entry = State.query.filter_by(user_id=current_user.id, key=FAVORITE_PRESETS_KEY).first()
        if state_entry and state_entry.value:
            favorites = state_entry.value if isinstance(state_entry.value, list) else []
            current_app.logger.info(f"[State Route] Retrieved {len(favorites)} favorite presets for user {current_user.id}")
            return jsonify(favorites)
        return jsonify([])
    except Exception as e:
        current_app.logger.error(f"[State Route] Error fetching favorite presets: {e}")
        return jsonify({"error": "Failed to retrieve favorite presets."}), 500

@user_state_bp.route(f"/{FAVORITE_PRESETS_KEY}", methods=["PUT"])
@crypto_auth_required
def set_favorite_presets():
    current_user = g.user
    data = request.get_json()
    if not isinstance(data, list):
        return jsonify({"error": "Request body must be a JSON array."}), 400
    try:
        state_entry = State.query.filter_by(user_id=current_user.id, key=FAVORITE_PRESETS_KEY).first()
        if not state_entry:
            state_entry = State(user_id=current_user.id, key=FAVORITE_PRESETS_KEY)
            db.session.add(state_entry)
        state_entry.value = data
        db.session.commit()
        return jsonify({"status": "success"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@user_state_bp.route(f"/{FAVORITE_COMPONENTS_KEY}", methods=["GET"])
@crypto_auth_required
def get_favorite_components():
    current_user = g.user
    try:
        state_entry = State.query.filter_by(user_id=current_user.id, key=FAVORITE_COMPONENTS_KEY).first()
        if state_entry and state_entry.value:
            favorites = state_entry.value if isinstance(state_entry.value, list) else []
            return jsonify(favorites)
        return jsonify([])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@user_state_bp.route(f"/{FAVORITE_COMPONENTS_KEY}", methods=["PUT"])
@crypto_auth_required
def set_favorite_components():
    current_user = g.user
    data = request.get_json()
    if not isinstance(data, list):
        return jsonify({"error": "Request body must be a JSON array."}), 400
    try:
        state_entry = State.query.filter_by(user_id=current_user.id, key=FAVORITE_COMPONENTS_KEY).first()
        if not state_entry:
            state_entry = State(user_id=current_user.id, key=FAVORITE_COMPONENTS_KEY)
            db.session.add(state_entry)
        state_entry.value = data
        db.session.commit()
        return jsonify({"status": "success"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@user_state_bp.route(f"/{ACTIVE_APPS_KEY}", methods=["GET"])
@user_state_bp.route(f"/{ACTIVE_WIDGETS_KEY}", methods=["GET"]) # [ZOMBIE_SUPPORT]
@crypto_auth_required
def get_active_apps():
    """Returns the list of currently open apps/widgets in the GUI."""
    current_user = g.user
    try:
        state_entry = State.query.filter_by(user_id=current_user.id, key=ACTIVE_APPS_KEY).first()

        if not state_entry:
            state_entry = State.query.filter_by(user_id=current_user.id, key=ACTIVE_WIDGETS_KEY).first()

        if state_entry and state_entry.value:
            apps_state = state_entry.value if isinstance(state_entry.value, list) else []
            return jsonify(apps_state)
        return jsonify([])
    except Exception as e:
        current_app.logger.error(f"[State Route] Error fetching active apps: {e}")
        return jsonify({"error": "Failed to retrieve active apps."}), 500

@user_state_bp.route(f"/{ACTIVE_APPS_KEY}", methods=["PUT"])
@user_state_bp.route(f"/{ACTIVE_WIDGETS_KEY}", methods=["PUT"]) # [ZOMBIE_SUPPORT]
@crypto_auth_required
def set_active_apps():
    """Syncs the list of open apps from GUI to database."""
    current_user = g.user
    data = request.get_json()

    if not isinstance(data, list):
        return jsonify({"error": "Request body must be a JSON array."}), 400

    try:
        state_entry = State.query.filter_by(user_id=current_user.id, key=ACTIVE_APPS_KEY).first()
        if not state_entry:
            state_entry = State(user_id=current_user.id, key=ACTIVE_APPS_KEY)
            db.session.add(state_entry)

        state_entry.value = data
        db.session.commit()

        current_app.logger.info(f"[State Route] Updated active apps for user {current_user.id}. Count: {len(data)}")
        return jsonify({"status": "success", "message": "Active apps synced."})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[State Route] Error saving active apps: {e}")
        return jsonify({"error": "Failed to save active apps."}), 500
