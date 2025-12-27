########################################################################
# WEBSITE https://flowork.cloud
# File NAME : C:\flowork-nano\apps\universal_downloader\backend\service.py total lines 157 
########################################################################

import os
import uuid
import asyncio
import json
import logging
import subprocess
import sys
import re
import time
import shutil
import glob
from pathlib import Path
from flowork_kernel.services.base_service import BaseService
from flowork_kernel.utils.path_helper import get_data_directory, resolve_user_path

yt_dlp = None

class UniversalDownloaderService(BaseService):
    def __init__(self, kernel, service_id: str):
        super().__init__(kernel, service_id)
        self.name = "Universal Downloader"
        self.active_jobs = {}
        self.kernel.write_to_log(f"Service '{service_id}' initialized.", "INFO")
        try:
            import yt_dlp as lib
            global yt_dlp
            yt_dlp = lib
        except: pass

    def _ensure_dependency(self):
        global yt_dlp
        try:
            import yt_dlp as lib
            yt_dlp = lib
            return True
        except ImportError:
            self.kernel.write_to_log(f"[{self.name}] ⚠️ yt_dlp missing. Installing...", "WARN")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "yt-dlp"])
                import yt_dlp as lib
                yt_dlp = lib
                self.kernel.write_to_log(f"[{self.name}] ✅ Dependency loaded.", "SUCCESS")
                return True
            except Exception as e:
                self.kernel.write_to_log(f"[{self.name}] ❌ Install Failed: {e}", "ERROR")
                return False

    def start(self):
        self.kernel.write_to_log(f"[{self.name}] Service Ready.", "SUCCESS")

    def stop(self):
        pass

    def _clean_ansi(self, text):
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return ansi_escape.sub('', text)

    def get_job_progress(self, job_id):
        if job_id in self.active_jobs:
            return self.active_jobs[job_id]
        return {"status": "idle", "percent": "0%", "speed": "0", "eta": "-"}

    def list_directory(self, path: str, user_id: str):
        return self.secure_list_directory(path, user_id)

    def create_folder(self, current_path: str, folder_name: str, user_id: str):
        return self.secure_create_folder(current_path, folder_name, user_id)

    def delete_path(self, target_path_str: str, user_id: str):
        return self.secure_delete_path(target_path_str, user_id)

    def start_download_task(self, url: str, user_id: str, options: dict):
        job_id = str(uuid.uuid4())[:8]
        self.active_jobs[job_id] = {
            "status": "starting", "url": url, "percent": "0%", "speed": "Init", "eta": "..."
        }
        return job_id

    def _cleanup_debris(self, folder, filename_base):
        """Menghapus file .part atau .ytdl sisa download"""
        try:
            pattern = os.path.join(folder, f"{filename_base}*")
            files = glob.glob(pattern)

            for f in files:
                if not f.endswith(('.mp4', '.mp3', '.mkv', '.wav')):
                    try:
                        os.remove(f)
                    except: pass
        except: pass

    def execute_download(self, job_id, raw_urls, user_id, options):
        if not yt_dlp:
            if not self._ensure_dependency():
                self.active_jobs[job_id]["status"] = "error"
                self.active_jobs[job_id]["error"] = "Dependency Missing"
                return

        custom_folder = options.get("output_folder")
        output_dir, user_jail = self._resolve_and_secure_path(custom_folder, user_id)

        if not output_dir.exists():
            output_dir.mkdir(parents=True, exist_ok=True)

        urls = [u.strip() for u in raw_urls.split('\n') if u.strip()]
        total_urls = len(urls)

        self.kernel.write_to_log(f"🚀 Job [{job_id}] Batch Size: {total_urls}", "INFO")

        def progress_hook(d):
            if d['status'] == 'downloading':
                p = self._clean_ansi(d.get('_percent_str', '0%')).strip()
                s = self._clean_ansi(d.get('_speed_str', '-')).strip()
                e = self._clean_ansi(d.get('_eta_str', '-')).strip()

                self.active_jobs[job_id].update({
                    "status": "downloading", "percent": p, "speed": s, "eta": e
                })

        for idx, single_url in enumerate(urls, 1):
            filename_str = str(idx) # "1", "2"
            try:
                target_file = output_dir / f"{filename_str}.%(ext)s"

                ydl_opts = {
                    'format': options.get('format', 'best'),
                    'outtmpl': str(target_file),
                    'quiet': True,
                    'no_warnings': True,
                    'progress_hooks': [progress_hook],
                    'socket_timeout': 30,
                    'keepvideo': False,
                    'nopart': False, # Pake part file biar resumeable, ntar kita bersihin manual
                    'merge_output_format': 'mp4' if options.get('format') != 'audio_mp3' else None
                }


                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(single_url, download=True)
                    final_name = ydl.prepare_filename(info)


                self._cleanup_debris(str(output_dir), filename_str)

            except Exception as e:
                self.kernel.write_to_log(f"❌ Failed Sequence {idx}: {e}", "ERROR")
                self._cleanup_debris(str(output_dir), filename_str)
                continue

        self.active_jobs[job_id]["status"] = "completed"
        self.active_jobs[job_id]["file"] = "Batch Complete"
