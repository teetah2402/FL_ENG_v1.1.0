########################################################################
# WEBSITE https://flowork.cloud
# File NAME : C:\flowork-nano\flowork-core\flowork_kernel\services\app_manager_service\app_manager_service.py
########################################################################

import os
import json
import importlib.util
import subprocess
import sys
import importlib.metadata
from ..base_service import BaseService
import zipfile
import tempfile
import shutil
import hashlib
from typing import Dict, List, Optional
from flask import request, send_file # - ADDED FOR API HANDLING

from flowork_kernel.models.ManifestModel import ManifestModel
from flowork_kernel.api_contract import BaseDashboardWidget

class AppManagerService(BaseService):

    def __init__(self, kernel, service_id: str):
        super().__init__(kernel, service_id)

        docker_internal_path = "/app/flowork_kernel/apps"
        win_local_path = r"C:\FLOWORK\apps"
        default_fallback = os.path.join(self.kernel.project_root_path, "flowork_kernel", "apps")

        if os.path.exists(docker_internal_path):
            self.apps_dir = docker_internal_path
            self.logger.info(f"AppManager: 🐳 Docker environment detected. Using mapped volume: {self.apps_dir}")
        elif sys.platform == 'win32':
            try:
                if not os.path.exists(win_local_path):
                    os.makedirs(win_local_path)
                self.apps_dir = win_local_path
                self.logger.info(f"AppManager: 🪟 Windows Local environment detected. Using path: {self.apps_dir}")
            except Exception as e:
                self.apps_dir = getattr(self.kernel, 'apps_path', default_fallback)
        else:
            self.apps_dir = getattr(self.kernel, 'apps_path', default_fallback)

        self.loaded_apps: Dict[str, Dict] = {}
        self.node_registry: Dict[str, Dict] = {}
        self.paused_status_file = os.path.join(self.kernel.data_path, "paused_apps.json")

    def discover_and_load_apps(self):
        self.logger.info(f"AppManager: Starting discovery in '{self.apps_dir}'...")
        discovered_apps = {}
        self.node_registry.clear()
        paused_ids = self._load_paused_status()

        if not os.path.exists(self.apps_dir): return

        try:
            items = os.listdir(self.apps_dir)
            for app_id in items:
                if app_id in self.kernel.globally_disabled_components: continue
                app_dir = os.path.join(self.apps_dir, app_id)

                if os.path.isdir(app_dir) and not app_id.startswith('__') and not app_id.startswith('.'):
                    self._install_app_dependencies(app_dir, app_id)
                    self._process_single_app(app_dir, app_id, paused_ids, discovered_apps)
        except Exception as e:
            self.logger.error(f"AppManager: Error scanning: {e}")

        self.loaded_apps = discovered_apps
        self.logger.warning(f"<<< FLOWORK V2 CORE >>> Loaded {len(self.loaded_apps)} apps & {len(self.node_registry)} nodes.")

    def _process_single_app(self, app_dir, app_id, paused_ids, target_dict):
        manifest_path = os.path.join(app_dir, "manifest.json")
        if not os.path.exists(manifest_path): return

        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            manifest = ManifestModel(**data)

            icon_raw = manifest.icon or (manifest.gui.icon if manifest.gui else "mdi-cube-outline")
            is_mdi = icon_raw.startswith("mdi-")

            for node in manifest.nodes:
                unique_node_id = f"{manifest.id}.{node.id}"
                node_type = getattr(node, "type", "action")

                if node_type == "trigger": category = "triggers"
                elif node_type == "ui": category = "tools"
                else: category = "modules"

                self.node_registry[unique_node_id] = {
                    "id": unique_node_id,
                    "app_id": manifest.id,
                    "category": category,
                    "node_def": node.dict(),
                    "label": node.label or node.name, # - Ensure label exists for frontend
                    "name": node.label or node.name,
                    "icon": node.icon or icon_raw,
                    "is_mdi": (node.icon or icon_raw).startswith("mdi-"),
                    "path": app_dir,
                    "is_installed": True
                }

            has_ui = manifest.gui.dashboard_enabled if manifest.gui else False
            entry_point = manifest.gui.dashboard_path if manifest.gui else "index.html"

            target_dict[app_id] = {
                "id": app_id,
                "name": manifest.name,
                "manifest": manifest.dict(),
                "path": app_dir,
                "is_paused": app_id in paused_ids or manifest.is_paused,
                "has_ui": has_ui,
                "entry_point": entry_point,
                "icon": icon_raw,
                "is_mdi": is_mdi,
                "tier": manifest.tier,
                "version": manifest.version,
                "is_installed": True
            }
        except Exception as e:
            self.logger.error(f" ! Failed to process Manifest V2 for '{app_id}': {e}")

    def get_app_icon_info(self, app_id):
        if app_id in self.loaded_apps:
            app = self.loaded_apps[app_id]
            manifest = app.get("manifest", {})
            icon_file = manifest.get("icon") or (manifest.get("gui", {}).get("icon") if manifest.get("gui") else "icon.svg")
            return {"icon_file": icon_file if not icon_file.startswith("mdi-") else "icon.svg"}
        return {"icon_file": "icon.svg"}

    def get_all_nodes(self) -> List[Dict]:
        return list(self.node_registry.values())

    def get_app_asset(self, app_id, filename):
        if app_id in self.loaded_apps:
            return os.path.join(self.loaded_apps[app_id]['path'], filename)
        return None

    def _install_app_dependencies(self, app_dir, app_id):
        req_file = os.path.join(app_dir, "requirements.txt")
        marker_file = os.path.join(app_dir, ".installed")
        if os.path.exists(req_file) and not os.path.exists(marker_file):
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", req_file], stdout=subprocess.DEVNULL)
                with open(marker_file, 'w') as f: f.write("installed")
            except: pass

    def _load_paused_status(self):
        if os.path.exists(self.paused_status_file):
            try:
                with open(self.paused_status_file, "r") as f: return json.load(f)
            except: return []
        return []

    # - ADDED: API Endpoints for Hybrid Apps and Node Registry
    def register_routes(self, router_bridge):
        # [English Hardcode] Mapping routes for Gateway tunneling

        @self.kernel.get_service("api_server_service").app.route('/api/v1/apps', methods=['GET'])
        def list_hybrid_apps():
            return {"status": "success", "data": list(self.loaded_apps.values())}

        @self.kernel.get_service("api_server_service").app.route('/api/v1/apps/nodes', methods=['GET'])
        def list_app_nodes():
            return {"status": "success", "data": self.get_all_nodes()}

        @self.kernel.get_service("api_server_service").app.route('/api/v1/apps/<app_id>/icon', methods=['GET'])
        def get_hybrid_app_icon(app_id):
            info = self.get_app_icon_info(app_id)
            asset_path = self.get_app_asset(app_id, info['icon_file'])
            if asset_path and os.path.exists(asset_path):
                return send_file(asset_path)
            return {"error": "Icon not found"}, 404