########################################################################
# WEBSITE https://flowork.cloud
# File NAME : C:\FLOWORK\flowork-core\flowork_kernel\services\app_runtime_service\execute_service_action.py total lines 115
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


async def run(hub, app_id: str, action_name: str, data: dict, retry_count=0, user_id=None):
    """
    Eksekutor Aksi Service: Mengirim perintah ke Daemon App via Socket. [cite: 245]
    Fix: Meneruskan user_id untuk Secret Injection (Roadmap Poin 4).
    Fix 2.0: Menangani ensure_app_running baik sync maupun async (Smart Await).
    """
    app_manager = hub.kernel.get_service('app_service')
    if not app_manager:
        app_manager = hub.kernel.get_service('app_manager_service')

    if not app_manager:
        hub.logger.error('AppManager not found!')
        return {'status': 'error', 'error': 'AppManager Unavailable'}

    try:
        # [Fase 3] Membangunkan App yang sedang tidur (Ghost Protocol) [cite: 402]
        port_or_coro = app_manager.ensure_app_running(app_id, user_id=user_id)

        if asyncio.iscoroutine(port_or_coro):
            port = await port_or_coro
        else:
            port = port_or_coro

    except Exception as e:
        return {'status': 'error', 'error': f'Failed to start App Daemon: {str(e)}'}

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.settimeout(15)

    try:
        loop = asyncio.get_running_loop()

        def socket_transaction():
            # [Fase 3] Immortal Bridge: Menghubungkan Socket ke Port App [cite: 179, 262]
            client.connect(('127.0.0.1', int(port)))

            # Tambahkan metadata user_id untuk keperluan Iron Bank (Data Access Layer) [cite: 309]
            request_payload = {
                'action': action_name,
                'data': data,
                'metadata': {'user_id': user_id, 'timestamp': time.time()}
            }

            payload = json.dumps(request_payload).encode('utf-8')
            client.sendall(struct.pack('!I', len(payload)))
            client.sendall(payload)

            # [Fase 3] Menerima balasan dari App Runner [cite: 267]
            header = client.recv(4)
            if not header:
                raise ConnectionResetError('Empty header')
            length = struct.unpack('!I', header)[0]

            chunks = []
            bytes_recd = 0
            while bytes_recd < length:
                chunk = client.recv(min(length - bytes_recd, 4096))
                if not chunk:
                    raise ConnectionResetError('Incomplete body')
                chunks.append(chunk)
                bytes_recd += len(chunk)

            response_json = b''.join(chunks).decode('utf-8')
            return json.loads(response_json)

        response = await loop.run_in_executor(None, socket_transaction)
        return response

    except (ConnectionRefusedError, ConnectionResetError, socket.timeout, socket.error) as e:
        # [Fase 3] Lazarus Protocol: Bangkitkan kembali App yang crash [cite: 272, 280]
        if retry_count < 1:
            hub.logger.warning(f'⚠️ [Lazarus] App {app_id} link failed. Attempting revival... ({str(e)})')
            kill_res = app_manager.kill_app(app_id)
            if asyncio.iscoroutine(kill_res):
                await kill_res

            await asyncio.sleep(1.5)
            # Rekursif: Coba lagi sekali setelah restart [cite: 277]
            return await hub.execute_async('execute_service_action', app_id, action_name, data, retry_count=1, user_id=user_id)
        else:
            hub.logger.error(f'💀 [Lazarus] App {app_id} is dead beyond revival.')
            return {'status': 'error', 'error': 'Service Unavailable (App crashed repeatedly)'}
    except Exception as e:
        hub.logger.error(f"❌ [SocketExec] Error: {e}")
        return {'status': 'error', 'error': str(e)}
    finally:
        try:
            client.close()
        except:
            pass