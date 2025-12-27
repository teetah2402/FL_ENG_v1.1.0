########################################################################
# WEBSITE https://flowork.cloud
# File NAME : C:\flowork-nano\flowork-core\flowork_kernel\services\api_server_service\dependencies.py total lines 127 
########################################################################

import sys
import importlib
import importlib.util
import logging
import inspect
from flowork_kernel.exceptions import PermissionDeniedError
from flowork_kernel.services.ai_provider_manager_service.ai_provider_manager_service import AIProviderManagerService
from flowork_kernel.services.app_manager_service.app_manager_service import AppManagerService
import os
import aiofiles

class DependenciesMixin:
    def _safe_get_service(self, service_id):
        try:
            return self.kernel.get_service(service_id)
        except PermissionDeniedError:
            self.kernel.write_to_log(
                f"ApiServer dependency '{service_id}' unavailable due to license tier.",
                "WARN",
            )
            return None
        except Exception:
            return None

    def _load_dependencies(self):
        self.kernel.write_to_log(
            "ApiServerService: Loading service dependencies...", "INFO"
        )

        self.variable_manager = self._safe_get_service("variable_manager_service")
        self.preset_manager = self._safe_get_service("preset_manager_service")
        self.state_manager = self._safe_get_service("state_manager")


        self.db_service = self._safe_get_service("database_service")
        self.prompt_manager_service = self._safe_get_service("prompt_manager_service")
        self.event_bus = self._safe_get_service("event_bus")
        self.workflow_executor = self._safe_get_service("workflow_executor_service")

        self.app_manager_service = self._safe_get_service("app_manager_service")
        self.widget_manager_service = self.app_manager_service

        if not self.app_manager_service:
            self.kernel.write_to_log("[ForceLoad] AppManagerService missing from Kernel. Initializing manually...", "WARN")
            try:
                self.app_manager_service = AppManagerService(self.kernel, "app_manager_service")
                self.kernel.register_service(self.app_manager_service)
                if hasattr(self.app_manager_service, 'discover_and_load_apps'):
                    self.app_manager_service.discover_and_load_apps()
                self.kernel.write_to_log("[ForceLoad] AppManagerService initialized & discovery triggered.", "SUCCESS")
                self.widget_manager_service = self.app_manager_service
            except Exception as e:
                self.kernel.write_to_log(f"[ForceLoad] Failed to init AppManagerService: {str(e)}", "ERROR")

        self.kernel.write_to_log("ApiServer: Checking AppLifecycleService status...", "DEBUG")
        lifecycle_svc = self._safe_get_service("app_lifecycle_service")

        if not lifecycle_svc:
            self.kernel.write_to_log("⚠️ [ForceLoad] AppLifecycleService not found in Registry. Starting manual injection...", "WARN")
            try:
                from flowork_kernel.services.app_lifecycle_service.app_lifecycle_service import AppLifecycleService
                lifecycle_svc = AppLifecycleService(self.kernel, "app_lifecycle_service")
                self.kernel.register_service(lifecycle_svc)
                if not hasattr(lifecycle_svc, 'loaded_apps'):
                    lifecycle_svc.loaded_apps = {}
                lifecycle_svc.start()
                self.kernel.write_to_log("✅ [ForceLoad] AppLifecycleService injected and started successfully!", "SUCCESS")
            except Exception as e:
                import traceback
                self.kernel.write_to_log(f"❌ [ForceLoad] FATAL: Failed to inject AppLifecycleService: {e}\n{traceback.format_exc()}", "CRITICAL")

        self.ai_provider_manager_service = self._safe_get_service("ai_provider_manager_service")
        if not self.ai_provider_manager_service:
            self.kernel.write_to_log("[ForceLoad] AIProviderManagerService missing from Kernel. Initializing manually...", "WARN")
            try:
                self.ai_provider_manager_service = AIProviderManagerService(self.kernel, "ai_provider_manager_service")
                self.kernel.register_service(self.ai_provider_manager_service)
                self.kernel.write_to_log("[ForceLoad] AIProviderManagerService initialized successfully.", "SUCCESS")
            except Exception as e:
                self.kernel.write_to_log(f"[ForceLoad] Failed to init AIProviderManagerService: {str(e)}", "ERROR")

        self.neural_ingestor_service = None

        self.kernel.write_to_log(
            "ApiServerService: All available service dependencies loaded (Lite Mode).", "SUCCESS"
        )

    async def _load_protected_component_ids(self):
        protected_ids = set()
        config_path = os.path.join(self.kernel.data_path, "protected_components.txt")
        try:
            try:
                async with aiofiles.open(config_path, "r", encoding="utf-8") as f:
                    content = await f.read()
            except ImportError:
                self.kernel.write_to_log(
                    f"aiofiles not found, reading protected_components.txt synchronously.", "WARN"
                )
                if os.path.exists(config_path):
                    with open(config_path, "r", encoding="utf-8") as f:
                        content = f.read()
                else:
                    content = ""
            protected_ids = {
                line.strip()
                for line in content.splitlines()
                if line.strip() and not line.startswith("FLOWORK")
            }
            self.kernel.write_to_log(
                f"Loaded {len(protected_ids)} protected component IDs.", "INFO"
            )
        except FileNotFoundError:
            self.kernel.write_to_log(
                f"Config 'protected_components.txt' not found. No components will be protected.",
                "WARN",
            )
        except Exception as e:
            self.kernel.write_to_log(
                f"Could not load protected component IDs: {e}", "ERROR"
            )
        return protected_ids
