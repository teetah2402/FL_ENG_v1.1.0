########################################################################
# WEBSITE https://flowork.cloud
# File NAME : C:\FLOWORK\flowork-core\flowork_kernel\services\app_runtime_service\trigger_event_handler.py total lines 65
##1. Dynamic Component Discovery (DCD): Hub wajib melakukan scanning file secara otomatis.
##2. Lazy Loading: Modul hanya di-import ke RAM saat dipanggil (On-Demand).
##3. Atomic Isolation: 1 File = 1 Fungsi dengan nama file yang identik dengan nama fungsi aslinya.
##4. Zero Logic Mutation: Dilarang merubah alur logika, nama variabel, atau struktur if/try/loop.
########################################################################

import os
import sys
import json
import time
import socket
import struct
import subprocess
import threading
import asyncio
import queue
import importlib.util
import concurrent.futures
from typing import Dict, Any
from flowork_kernel.services.base_service import BaseService


def run(hub, app_id: str, action_name: str, payload: dict):
    """
    Triggers an event reaction inside an app runner instance via Phase 3 Socket Bridge.
    Fix: Menggunakan execute_async untuk fungsi async agar coroutine dijalankan.
    """
    try:
        hub.logger.info(f"🧠 [NeuralSpike] Triggering reaction: {app_id} -> {action_name}")

        loop = None
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            pass

        # [PHASE 5] Fire and Forget: Jangan biarkan Kernel menunggu proses di App selesai
        if loop and loop.is_running():
            # [PHASE 3 Integration] execute_service_action sudah mendukung Lazarus (Auto-Wake)
            # Kita panggil secara asinkron agar loop utama Kernel tetap ringan
            loop.create_task(hub.execute_async('execute_service_action', app_id, action_name, payload))
        else:
            # Jalur darurat jika dipanggil dari konteks Non-Async (Threaded)
            def fire_and_forget():
                try:
                    # Buat loop baru khusus untuk pengiriman paket saraf ini
                    new_loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(new_loop)
                    # Pastikan execute_service_action dipanggil sampai tuntas
                    new_loop.run_until_complete(hub.execute_async('execute_service_action', app_id, action_name, payload))
                    new_loop.close()
                except Exception as ex:
                    hub.logger.error(f"🔥 [Nervous-Spike] Threaded Dispatch Fail for {app_id}: {ex}")

            # Gunakan Daemon Thread agar tidak menahan shutdown Kernel
            threading.Thread(target=fire_and_forget, daemon=True, name=f"Spike-{app_id}").start()

    except Exception as e:
        hub.logger.error(f'❌ [Nervous] Failed to trigger event for {app_id}: {e}')