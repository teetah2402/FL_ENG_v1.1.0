########################################################################
# WEBSITE https://flowork.cloud
# File NAME : C:\FLOWORK\flowork-gateway\app\sockets.py
# REFACTORED: Plug-and-Play Nano Modules (Updated for Part 5)
########################################################################

import logging
from flask import request, current_app
from .extensions import socketio as sio
from .socket_handlers import utils, auth, engine, workflow, resources, agent, swarm, hybrid

# --- REGISTER ALL HANDLERS ---
# Urutan registrasi handlers

# 1. Auth Handlers (Connect/Disconnect)
auth.register_handlers(sio)

# 2. Engine Logic (Heartbeat, Vitals)
engine.register_handlers(sio)

# 3. Workflow Logic (Execute, Stop, Pause)
workflow.register_handlers(sio)

# 4. Resource Management (Presets, Variables, Components, Settings)
resources.register_handlers(sio)

# 5. Agent & AI Logic (Chat, Tools)
agent.register_handlers(sio)

# 6. Swarm Tasking (R6 Protocol)
swarm.register_handlers(sio)

# 7. Hybrid Bridge (Browser <-> Python)
hybrid.register_handlers(sio)

# --- CATCH-ALL HANDLER ---
@sio.on('*', namespace='/gui-socket')
def on_gui_catch_all(event, data):
    app = current_app._get_current_object()
    sid = request.sid

    # List event yang VALID dan diketahui (supaya tidak dianggap anomaly)
    known = {
        # Basic
        'connect', 'disconnect', 'gui:join', 'gui:input',

        # Resources
        'request_presets_list', 'request_variables', 'request_components_list',
        'save_preset', 'load_preset', 'delete_preset',
        'request_settings', 'save_settings',
        'update_variable', 'delete_variable',
        'install_component', 'uninstall_component',

        # AI & Datasets
        'request_ai_status', 'request_datasets_list', 'request_local_models',
        'request_training_job_status', 'request_prompts_list',
        'update_prompt', 'delete_prompt',
        'request_dataset_data', 'create_dataset', 'add_dataset_data',
        'delete_dataset', 'update_dataset_row', 'delete_dataset_row',
        'start_training_job',

        # Workflow Execution
        'execute_workflow', 'stop_workflow', 'pause_workflow',
        'response_load_preset', 'execute_standalone_node',

        # Hybrid & Filesystem (NEW)
        'app_action_response',
        'filesystem_list_request',
        'filesystem_create_folder',
        'filesystem_delete',
        'filesystem_move',
        'filesystem_read',
        'filesystem_write'
    }

    gui_sess = utils._safe_get_session(sid, namespace='/gui-socket')
    user_id = gui_sess.get('user_id') if gui_sess else 'Anonymous'

    if event not in known:
        # Cuma warn kalau event bener-bener asing
        app.logger.warning(f"[Gateway GUI] ⚠️ Unhandled/Unknown event '{event}' from SID {sid} (User: {user_id}). Data: {data}")