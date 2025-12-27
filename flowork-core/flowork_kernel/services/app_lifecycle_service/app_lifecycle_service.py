########################################################################
# WEBSITE https://flowork.cloud
# File NAME : C:\flowork-nano\flowork-core\flowork_kernel\services\app_lifecycle_service\app_lifecycle_service.py total lines 135 
########################################################################

import importlib.util
import sys
import os
import time
import subprocess
import threading
import asyncio
import inspect
from pathlib import Path
from flowork_kernel.services.base_service import BaseService
from flowork_kernel.utils.path_helper import get_apps_directory

class AppLifecycleService(BaseService):
    def __init__(self, kernel=None, service_id="app_lifecycle_service"):
        if kernel:
            super().__init__(kernel, service_id)

        self.name = "app_lifecycle_service"
        self.loaded_apps = {}
        self.description = "The Grand Architect Factory: Loads external apps dynamically."

    def start(self):
        self.logger.info("🏭 [AppFactory] Starting The Engine...")
        self.logger.info(f"🏭 [AppFactory] Target Directory: {get_apps_directory()}")

        time.sleep(1)
        self._discover_and_load_apps()

    def _discover_and_load_apps(self):
        apps_dir = get_apps_directory()

        if not apps_dir.exists():
            try:
                os.makedirs(apps_dir, exist_ok=True)
                self.logger.info(f"✅ [AppFactory] Created missing apps directory at: {apps_dir}")
            except Exception as e:
                self.logger.error(f"❌ [AppFactory] FATAL: Cannot create apps dir: {e}")
                return

        self.logger.info(f"🔍 [AppFactory] Scanning for Apps in: {apps_dir}...")

        count = 0
        for app_name in os.listdir(apps_dir):
            app_path = apps_dir / app_name
            manifest_path = app_path / "manifest.json"
            service_path = app_path / "backend" / "service.py"

            if app_path.is_dir() and manifest_path.exists():
                try:
                    self._check_and_install_deps(app_path)

                    if service_path.exists():
                        self.logger.info(f"🚀 [AppFactory] Found Backend App: {app_name}. Injecting...")
                        if self._dynamic_import_service(app_name, service_path):
                            count += 1
                    else:
                        self.logger.info(f"🎨 [AppFactory] Found Frontend-Only App: {app_name}")

                except Exception as e:
                    self.logger.error(f"❌ [AppFactory] Failed to load App {app_name}: {str(e)}")

        self.logger.info(f"🏭 [AppFactory] Initialization Complete. Loaded {count} Apps.")

    def _check_and_install_deps(self, app_path):
        req_file = app_path / "requirements.txt"
        flag_file = app_path / ".installed"

        if req_file.exists() and not flag_file.exists():
            self.logger.warning(f"📦 [AppFactory] Installing dependencies for {app_path.name}...")
            try:
                subprocess.check_call([
                    sys.executable, "-m", "pip", "install", "-r", str(req_file)
                ])
                with open(flag_file, 'w') as f:
                    f.write("OK")
                self.logger.info(f"✅ [AppFactory] Dependencies installed for {app_path.name}")
            except subprocess.CalledProcessError as e:
                self.logger.error(f"❌ [AppFactory] Failed to install deps for {app_path.name}: {e}")

    def _dynamic_import_service(self, app_id, file_path):
        try:
            spec = importlib.util.spec_from_file_location(f"apps.{app_id}.service", str(file_path))
            if not spec or not spec.loader:
                self.logger.error(f"❌ [AppFactory] Could not load spec for {app_id}")
                return False

            module = importlib.util.module_from_spec(spec)
            sys.modules[f"apps.{app_id}.service"] = module
            spec.loader.exec_module(module)

            found_class = False
            for attribute_name in dir(module):
                attribute = getattr(module, attribute_name)

                if (isinstance(attribute, type) and
                    issubclass(attribute, BaseService) and
                    attribute is not BaseService):

                    try:
                        new_service = attribute(self.kernel, f"app_{app_id}")
                    except TypeError:
                        new_service = attribute()
                        new_service.kernel = self.kernel
                        new_service.service_id = f"app_{app_id}"

                    if not hasattr(new_service, 'logger'):
                         new_service.logger = self.logger

                    self.logger.info(f"⚡ [AppFactory] Starting Service: {new_service.name}...")

                    if hasattr(new_service, 'start'):
                        if inspect.iscoroutinefunction(new_service.start):
                            threading.Thread(target=asyncio.run, args=(new_service.start(),), daemon=True).start()
                            self.logger.info(f"🛰️ [AppFactory] {new_service.name} moved to Async Thread.")
                        else:
                            threading.Thread(target=new_service.start, daemon=True).start()
                            self.logger.info(f"🚀 [AppFactory] {new_service.name} moved to Sync Thread.")

                    self.loaded_apps[app_id] = new_service
                    found_class = True
                    return True

            if not found_class:
                self.logger.warning(f"⚠️ [AppFactory] No 'BaseService' subclass found in {file_path}")
                return False

        except Exception as e:
            self.logger.error(f"❌ [AppFactory] Injection Error for {app_id}: {e}", exc_info=True)
            return False
