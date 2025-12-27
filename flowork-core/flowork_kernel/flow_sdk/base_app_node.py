########################################################################
# WEBSITE https://flowork.cloud
# File NAME : C:\flowork-nano\flowork-core\flowork_kernel\flow_sdk\base_app_node.py total lines 171 
########################################################################

import os
import time
import uuid
import logging
from abc import ABC, abstractmethod

class BaseAppNode(ABC):
    """
    Base Class untuk semua App Node di Flowork.
    Menyediakan fitur:
    - Hybrid Interop (Komunikasi Python <-> Browser)
    - Multi-Tenancy (User Workspace Isolation)
    - Manifest V2 Awareness
    """
    def __init__(self, context=None):
        self.context = context or {}
        self.logger = getattr(context, 'logger', logging.getLogger("BaseAppNode"))
        self.kernel = getattr(context, 'kernel', None)

        self.manifest_def = self.context.get("node_def", {})

        if not self.kernel and isinstance(context, dict):
            self.kernel = context.get('kernel')

        self.user_id = "default_user"
        if isinstance(self.context, dict) and "user_context" in self.context:
             uc = self.context["user_context"]
             if uc and isinstance(uc, dict):
                 self.user_id = uc.get("user_id", "default_user")

        if os.getenv("FLOWORK_USER_ID"):
             self.user_id = os.getenv("FLOWORK_USER_ID")

        self.base_data_dir = os.getenv("FLOWORK_DATA_DIR", "./data")

        self.user_workspace = os.path.join(self.base_data_dir, "users", self.user_id)
        self._ensure_workspace()

    def _ensure_workspace(self):
        """Memastikan folder user ada sebelum dipakai."""
        if not os.path.exists(self.user_workspace):
            try:
                os.makedirs(self.user_workspace, exist_ok=True)
            except Exception as e:
                self.logger.error(f"[SDK] Failed to create workspace: {e}")

    def get_file_path(self, filename: str) -> str:
        """
        [SECURE PATH RESOLVER]
        Mengubah 'laporan.txt' menjadi 'C:/FLOWORK/data/users/user123/laporan.txt'
        Mencegah Directory Traversal (../)
        """
        clean_name = os.path.basename(filename)
        return os.path.join(self.user_workspace, clean_name)

    def save_text(self, filename: str, content: str):
        """Helper praktis untuk simpan text ke user workspace."""
        path = self.get_file_path(filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        self.logger.info(f"[SDK] Saved to: {path}")
        return path

    def load_text(self, filename: str) -> str:
        """Helper praktis untuk baca text dari user workspace."""
        path = self.get_file_path(filename)
        if not os.path.exists(path):
            return None
        with open(path, "r", encoding="utf-8") as f:
            return f.read()


    def get_arg(self, inputs: dict, name: str, default=None):
        """
        Retrieves a value from inputs safely.
        Priority:
        1. Direct input (runtime payload)
        2. Config defined in Manifest (if available/defaults)
        3. Provided default value
        """
        val = inputs.get(name)
        if val is not None:
            return val

        if self.manifest_def:
            for field in self.manifest_def.get("inputs", []):
                if field.get("name") == name:
                    return field.get("default", default)

        return default

    def set_output(self, port_name: str, data: any) -> dict:
        """
        Standard way to structure output for a specific port.
        """
        return {port_name: data}

    @abstractmethod
    def execute(self, inputs):
        """
        Method ini WAJIB di-override oleh App Developer (Subclass).
        """
        raise NotImplementedError("App Node must implement execute()")

    def request_frontend_action(self, action_name, payload, timeout=60):
        """
        JURUS HYBRID:
        1. Pause Python.
        2. Kirim sinyal ke Browser User via EventBus -> Gateway.
        3. Tunggu Browser bales (Polling memory).
        4. Lanjut Python.
        """
        if not self.kernel:
            self.logger.warning("Kernel context missing. Hybrid features might fail.")

        event_bus = None
        if self.kernel:
            event_bus = self.kernel.get_service("event_bus")

        if not event_bus:
            self.logger.error("EventBus service missing. Cannot signal Frontend.")
            return None

        job_id = "unknown"
        if isinstance(self.context, dict):
             job_id = self.context.get("job_id", "unknown_job")

        request_id = f"req_{job_id}_{uuid.uuid4().hex[:8]}"

        session_id = "broadcast"
        if isinstance(self.context, dict) and "user_context" in self.context:
             uc = self.context["user_context"]
             if uc and isinstance(uc, dict):
                 session_id = uc.get("session_id", "broadcast")

        self.logger.info(f"🌉 [HybridBridge] Requesting Frontend Action: {action_name} (ID: {request_id})")

        event_bus.publish(
            "HYBRID_ACTION_REQUEST",
            {
                "request_id": request_id,
                "target_session": session_id,
                "app_id": getattr(self, 'app_id', 'unknown_app'),
                "action": action_name,
                "payload": payload
            }
        )

        if self.kernel:
            if not hasattr(self.kernel, "memory_store"):
                self.kernel.memory_store = {}

            start_time = time.time()
            while time.time() - start_time < timeout:
                response_key = f"response_{request_id}"

                if response_key in self.kernel.memory_store:
                    result = self.kernel.memory_store.pop(response_key)
                    self.logger.info(f"✅ [HybridBridge] Received Response for {request_id}")
                    return result

                time.sleep(0.5) # Cek setiap 500ms

            self.logger.error(f"❌ [HybridBridge] Timeout waiting for Frontend Action: {action_name}")
            raise TimeoutError(f"Frontend did not respond to '{action_name}' within {timeout}s.")
