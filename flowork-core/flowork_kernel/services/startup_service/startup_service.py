########################################################################
# WEBSITE https://flowork.cloud
# File NAME : C:\flowork-nano\flowork-core\flowork_kernel\services\startup_service\startup_service.py total lines 189 
########################################################################

from ..base_service import BaseService
import time
import asyncio
import subprocess
import sys
import os
from flowork_kernel.exceptions import (
    MandatoryUpdateRequiredError,
    PermissionDeniedError,
)

class StartupService(BaseService):

    def __init__(self, kernel, service_id: str):
        super().__init__(kernel, service_id)
        pass

    async def run_startup_sequence(self):

        try:
            self.logger.info("StartupService (Phase 1): Pre-flight checks (Lite Mode)...")


            integrity_checker = self.kernel.get_service(
                "integrity_checker_service", is_system_call=True
            )
            if integrity_checker:
                integrity_checker.verify_core_files()

            self._auto_install_dependencies()

            self.logger.info(
                "StartupService (Phase 2): Starting ESSENTIAL LITE services..."
            )

            essential_services_to_start = {
                "api_server_service": None,


                "app_manager_service": lambda s: s.discover_and_load_apps(), # Replaces widget_manager
                "preset_manager_service": lambda s: s.start(),
                "localization_manager": lambda s: s.load_all_languages(),
                "gateway_connector_service": None,
            }

            for service_id, start_action in essential_services_to_start.items():
                try:
                    service_instance = self.kernel.get_service(
                        service_id, is_system_call=True
                    )
                    if service_instance:
                        if (
                            start_action is None
                            and hasattr(service_instance, "start")
                            and asyncio.iscoroutinefunction(service_instance.start)
                        ):
                            await service_instance.start()
                        elif (
                            start_action is None
                            and hasattr(service_instance, "start")
                            and not asyncio.iscoroutinefunction(service_instance.start)
                        ):
                            service_instance.start()
                        elif start_action:
                            start_action(service_instance)
                except Exception as e:
                    self.logger.error(
                        f"[LITE BOOT] Failed to start {service_id}: {e}"
                    )

            self.logger.info(
                "StartupService (Phase 3): Skipping User/License Checks (Open Core Mode)..."
            )
            self.kernel.current_user = None

            self.logger.info(
                "StartupService (Phase 4): Finalizing..."
            )

            self.logger.info(
                "StartupService: Checking for background service plugins (Skipped in Lite)..."
            )

            time.sleep(1)
            event_bus = self.kernel.get_service("event_bus", is_system_call=True)
            if event_bus:
                event_bus.publish("event_all_services_started", {})
            self.kernel.startup_complete = True

            self.logger.info("✅ [BOOT SUCCESS] Flowork LITE Core is ready.")
            return {"status": "complete"}

        except MandatoryUpdateRequiredError:
            raise
        except Exception as e:
            self.logger.critical(f"CRITICAL BOOT ERROR: {e}")
            import traceback
            self.logger.debug(traceback.format_exc())
            raise e

    def _attempt_auto_login(self):
        pass

    def _get_real_root_path(self):
        """Cerdas menentukan root path (Docker vs Local)"""

        kernel_path = getattr(self.kernel, "project_root_path", None)

        if kernel_path:
             return kernel_path

        return os.getcwd()

    def _auto_install_dependencies(self):
        root_path = self._get_real_root_path()

        self.logger.info(f"🔍 [Auto-Installer] Initializing Scan on Root: {root_path}")

        target_dirs = [
            'apps',
            'ai_providers'
        ]

        install_count = 0

        for category in target_dirs:
            base_path = os.path.join(root_path, category)

            if not os.path.exists(base_path):
                continue

            try:
                items = os.listdir(base_path)
            except Exception as e:
                continue

            for item_name in items:
                item_path = os.path.join(base_path, item_name)

                if not os.path.isdir(item_path) or item_name.startswith('.') or item_name.startswith('__'):
                    continue

                req_file = os.path.join(item_path, "requirements.txt")
                flag_file = os.path.join(item_path, ".installed")

                if os.path.exists(req_file):
                    should_install = True
                    if os.path.exists(flag_file):
                        try:
                            req_mtime = os.path.getmtime(req_file)
                            flag_mtime = os.path.getmtime(flag_file)
                            if req_mtime < flag_mtime:
                                should_install = False
                        except:
                            should_install = True

                    if should_install:
                        self.logger.info(f"📦 [Auto-Installer] Installing dependencies for: {category}/{item_name}...")
                        try:
                            cmd = [
                                sys.executable, "-m", "pip", "install",
                                "-r", req_file,
                                "--disable-pip-version-check",
                                "--prefer-binary"
                            ]

                            process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

                            if process.returncode == 0:
                                with open(flag_file, 'w') as f:
                                    f.write(f"Installed on {time.ctime()}")
                                self.logger.info(f"✅ [Auto-Installer] Success: {item_name}")
                                install_count += 1
                            else:
                                self.logger.error(f"❌ [Auto-Installer] FAILED: {item_name}")

                        except Exception as e:
                            self.logger.error(f"❌ [Auto-Installer] Unexpected Error {item_name}: {e}")

        if install_count > 0:
            self.logger.info(f"✨ [Auto-Installer] Complete. Installed dependencies for {install_count} components.")
        else:
            self.logger.info("⚡ [Auto-Installer] System up-to-date.")
