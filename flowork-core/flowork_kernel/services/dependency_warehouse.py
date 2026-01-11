########################################################################
# WEBSITE https://flowork.cloud
# File NAME : C:\FLOWORK\flowork-core\flowork_kernel\services\dependency_warehouse.py
##1. Immutability: Folder global_libs hanya boleh dibaca oleh App. [cite: 4, 5]
##2. Version Isolation: Simpan lib berdasarkan versi (global_libs/lib/version). [cite: 7, 8]
##3. Path Injection: Core membisikkan alamat lib ke Python Runner. [cite: 11]
########################################################################

import os
import sys
import hashlib
import subprocess
import logging
from flowork_kernel.services.base_service import BaseService

class DependencyWarehouse(BaseService):
    def __init__(self, kernel, service_id: str):
        super().__init__(kernel, service_id)
        self.logger = logging.getLogger("Kernel.Warehouse")
        # Folder suci tempat semua library berkumpul [cite: 4]
        self.warehouse_path = os.path.join(self.kernel.data_path, "global_libs")
        os.makedirs(self.warehouse_path, exist_ok=True)

    def resolve_and_install(self, lib_name: str, version: str = "latest"):
        """
        Mengecek ketersediaan lib di gudang, jika tidak ada, download otomatis. [cite: 16, 19]
        """
        target_dir = os.path.join(self.warehouse_path, lib_name.lower(), version)

        if not os.path.exists(target_dir):
            self.logger.info(f"⬇️ [Warehouse] Library {lib_name} ({version}) not found. Fetching...")
            os.makedirs(target_dir, exist_ok=True)
            try:
                # Install ke folder spesifik tanpa mengotori Core [cite: 18]
                req = f"{lib_name}=={version}" if version != "latest" else lib_name
                subprocess.check_call([
                    sys.executable, "-m", "pip", "install",
                    req, "--target", target_dir, "--no-cache-dir"
                ])
                self.logger.info(f"✅ [Warehouse] {lib_name} is now stored in {target_dir}")
            except Exception as e:
                self.logger.error(f"❌ [Warehouse] Failed to fetch {lib_name}: {e}")
                return None

        return target_dir

    def get_injection_paths(self, requirements: list):
        """
        Memberikan daftar path library untuk 'dibisikkan' ke Runner. [cite: 11, 20]
        """
        paths = []
        for req in requirements:
            # Parsing sederhana name==version
            parts = req.split('==')
            name = parts[0].strip()
            version = parts[1].strip() if len(parts) > 1 else "latest"
            path = self.resolve_and_install(name, version)
            if path: paths.append(path)
        return paths