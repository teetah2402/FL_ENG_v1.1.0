########################################################################
# WEBSITE https://flowork.cloud
# File NAME : C:\FLOWORK\ai_providers\text\chatgpt_provider\provider.py
########################################################################

import os
import inspect
import logging
import sqlite3 # [ADDITION] Untuk Direct DB Access

try:
    from flowork_kernel.api_contract import BaseAIProvider
except ImportError:
    from ai_providers.BaseAIProvider import BaseAIProvider

from .core.ChatGPTConnection import ChatGPTConnection

class ChatGPTProvider(BaseAIProvider):

    def __init__(self, kernel, manifest: dict):
        super().__init__(kernel, manifest)
        self.connection = ChatGPTConnection(self.kernel)

    def list_available_models(self) -> list:
        return ["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"]

    def _iron_bank_fetch(self, key_name, user_id=None):
        """
        [ADDITION] Meniru logic chatgpt_app: Ambil rahasia langsung dari DB
        untuk menghindari error 'MockKernel has no attribute variable_manager'.
        """
        db_paths = ["/app/data/flowork_core.db", "C:\\FLOWORK\\data\\flowork_core.db"]
        db_path = next((p for p in db_paths if os.path.exists(p)), None)
        if not db_path: return None

        try:
            # Buka dalam mode Read-Only (ro) agar tidak mengunci database
            conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
            cursor = conn.cursor()

            # Deteksi nama kolom secara dinamis (Tiru AI Council)
            cursor.execute("PRAGMA table_info(variables)")
            cols = [c[1] for c in cursor.fetchall()]
            key_col = next((x for x in ["name", "key", "variable_name"] if x in cols), "name")
            val_col = "value" if "value" in cols else "val"

            # Query dengan prioritas User ID
            if user_id:
                cursor.execute(f"SELECT {val_col} FROM variables WHERE {key_col} = ? AND user_id = ? LIMIT 1", (key_name, user_id))
                row = cursor.fetchone()
                if row: return row[0]

            # Fallback ke Global Variable
            cursor.execute(f"SELECT {val_col} FROM variables WHERE {key_col} = ? AND user_id IS NULL LIMIT 1", (key_name,))
            row = cursor.fetchone()
            conn.close()
            return row[0] if row else None
        except:
            return None

    def get_provider_name(self) -> str:
        return self.loc.get("chatgpt_provider_name", fallback="OpenAI ChatGPT")

    def is_ready(self, user_id=None, **kwargs) -> tuple[bool, str]:
        """
        [REINFORCED] Direct Database Secret Injection (Anti-MockKernel Error).
        """
        uid = user_id or kwargs.get('user_id')

        # 1. Coba lewat Service Manager dulu (Standard Path)
        api_key = None
        try:
            if hasattr(self.kernel, 'get_service'):
                var_service = self.kernel.get_service('variable_manager')
                if var_service:
                    api_key = var_service.get_variable("OPENAI_API_KEY", user_id=uid)
        except:
            # Jika MockKernel atau service belum init, api_key tetap None
            pass

        # 2. Jika gagal, gunakan IronBank Logic (Direct Path - Tiru ChatGPT App)
        if not api_key:
            api_key = self._iron_bank_fetch("OPENAI_API_KEY", user_id=uid)

        # 3. Injeksi ke OS Environ agar Connection bisa membaca
        if api_key:
            os.environ["OPENAI_API_KEY"] = str(api_key)

        # 4. Inisialisasi Connection
        try:
            sig = inspect.signature(self.connection.configure)
            if 'user_id' in sig.parameters:
                success = self.connection.configure(user_id=uid)
            else:
                success = self.connection.configure()

            if success: return (True, "")
        except Exception as e:
            return (False, f"Connection Configuration Error: {str(e)}")

        return (False, "ChatGPT API Key not found in Neural Vault or Database.")

    def generate_response(self, prompt: str, stream: bool = False, **kwargs) -> dict:
        user_id = kwargs.get('user_id')
        is_ready, message = self.is_ready(user_id=user_id)
        if not is_ready:
            return {"status": "error", "message": message}

        messages = kwargs.get('messages', None)
        target_model = kwargs.get('model', 'gpt-4o')

        try:
            if stream:
                return self._stream_response(prompt, messages)
            else:
                response_dict = self.connection.get_chat_completion(prompt, model=target_model, messages=messages)
                if "error" in response_dict:
                    return {"status": "error", "message": f"CHATGPT_API_ERROR: {response_dict['error']}"}
                return {"status": "success", "data": response_dict["data"]}
        except Exception as e:
            return {"status": "error", "message": f"Critical ChatGPT Error: {str(e)}"}

    def get_embedding(self, text: str) -> list:
        return self.connection.get_embeddings(text)

    def _stream_response(self, prompt, messages=None):
        if hasattr(self.connection, 'get_chat_stream'):
            iterator = self.connection.get_chat_stream(prompt, messages=messages)
            for chunk in iterator: yield chunk
        else: yield "[Streaming not supported]"