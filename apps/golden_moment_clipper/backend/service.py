########################################################################
# WEBSITE https://flowork.cloud
# File NAME : C:\flowork-nano\apps\golden_moment_clipper\backend\service.py total lines 372 
########################################################################

import os
import sys
import uuid
import shutil
import re
import traceback
import subprocess
import time
import importlib
from flowork_kernel.services.base_service import BaseService

WhisperModel = None
mp_face = None
cv2 = None

class GoldenMomentService(BaseService):
    def __init__(self, kernel, service_id: str):
        super().__init__(kernel, service_id)
        self.name = "Golden Moment Studio"
        self.ffmpeg_path, self.ffprobe_path = self._find_ffmpeg_tools()
        self.active_jobs = {}
        self.whisper_cache = {}

    def _find_ffmpeg_tools(self):
        return shutil.which("ffmpeg") or "ffmpeg", shutil.which("ffprobe") or "ffprobe"

    def _ensure_dependencies(self, job_id):
        global WhisperModel, mp_face, cv2
        if WhisperModel and mp_face and cv2: return True

        self.log_job(job_id, "⚙️ Checking AI Dependencies...", "info")

        need_reinstall = False
        try:
            import av
            import faster_whisper
            import mediapipe
            _ = mediapipe.solutions.face_detection
        except (ImportError, AttributeError, RuntimeError):
            need_reinstall = True
            self.log_job(job_id, "⚠️ Library incompatibility detected. Updating...", "warn")

        if need_reinstall:
            try:
                pkgs_del = ["av", "faster-whisper", "mediapipe", "protobuf"]
                subprocess.call([sys.executable, "-m", "pip", "uninstall", "-y"] + pkgs_del, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

                cmds = [
                    "protobuf==3.20.3",
                    "mediapipe==0.10.9",
                    "faster-whisper>=1.0.0",
                    "opencv-python-headless",
                    "numpy<2.0.0"
                ]

                for c in cmds:
                    self.log_job(job_id, f"📦 Installing: {c}...", "info")
                    subprocess.check_call([sys.executable, "-m", "pip", "install", c], stdout=subprocess.DEVNULL)

                importlib.invalidate_caches()
            except Exception as e:
                self.log_job(job_id, f"❌ Install Failed: {e}", "error")
                return False

        try:
            for m in ['av', 'faster_whisper', 'mediapipe', 'google.protobuf']:
                if m in sys.modules: del sys.modules[m]

            import faster_whisper
            WhisperModel = faster_whisper.WhisperModel
            import cv2 as cv2_lib
            cv2 = cv2_lib
            import mediapipe as mp
            mp_face = mp.solutions.face_detection

            self.log_job(job_id, "🚀 AI Engine Loaded!", "success")
            return True
        except Exception as e:
            self.log_job(job_id, f"❌ Load Error: {e}", "error")
            traceback.print_exc()
            return False

    def list_directory(self, path: str, user_id: str):
        return self.secure_list_directory(path, user_id)

    def init_job(self, user_id):
        job_id = uuid.uuid4().hex[:8]
        self.active_jobs[job_id] = {"status": "running", "user_id": user_id, "logs": [], "created_at": time.time()}
        return job_id

    def log_job(self, job_id, msg, type="info"):
        if job_id in self.active_jobs:
            print(f"[{job_id}] {msg}")
            self.active_jobs[job_id]["logs"].append({"msg": msg, "type": type})

    def get_job_status(self, job_id):
        if job_id not in self.active_jobs: return {"status": "unknown"}
        job = self.active_jobs[job_id]
        logs = list(job["logs"])
        job["logs"] = []
        return {"status": job["status"], "logs": logs}

    def run_process_safe(self, job_id, config, user_id):
        try:
            self.process_video_logic(job_id, config, user_id)
            self.active_jobs[job_id]["status"] = "completed"
            self.log_job(job_id, "✅ All Batch Tasks Completed.", "success")
        except Exception as e:
            traceback.print_exc()
            self.active_jobs[job_id]["status"] = "failed"
            self.log_job(job_id, f"❌ CRITICAL ERROR: {str(e)}", "error")

    def process_video_logic(self, job_id, config, user_id):
        if not self._ensure_dependencies(job_id): raise Exception("Dependency Error")

        input_path_raw = config.get("input_folder_path")
        output_folder_base = config.get("output_folder")
        outro_path = config.get("outro_path")

        if not input_path_raw or not os.path.exists(input_path_raw):
            raise Exception(f"Input path invalid: {input_path_raw}")

        videos = []
        if os.path.isfile(input_path_raw):
            videos = [input_path_raw]
            self.log_job(job_id, "📂 Mode: Single File Processing", "info")
        else:
            files = [f for f in os.listdir(input_path_raw) if f.lower().endswith(('.mp4','.mov','.avi','.mkv'))]
            files.sort()
            videos = [os.path.join(input_path_raw, f) for f in files]
            self.log_job(job_id, f"📂 Mode: Batch Folder ({len(videos)} videos)", "info")

        if not videos: raise Exception("No videos found.")
        if not os.path.exists(output_folder_base): os.makedirs(output_folder_base, exist_ok=True)

        timestamps_raw = config.get("timestamps", "")
        tasks = {}

        for line in timestamps_raw.split('\n'):
            line = line.strip()
            if not line: continue

            parts = line.split('|')
            time_part = parts[0].strip()

            if len(parts) >= 2:
                vid_id = parts[1].strip() # Pake ID dari user
            else:
                vid_id = "1" # Default ke Video No. 1

            t_parts = time_part.split('-')
            if len(t_parts) == 2:
                s = self._parse_time(t_parts[0].strip())
                e = self._parse_time(t_parts[1].strip())
                if s is not None and e is not None:
                    if vid_id not in tasks: tasks[vid_id] = []
                    tasks[vid_id].append((s, e))

        if not tasks: raise Exception("No valid timestamps found.")

        final_outro = None
        if outro_path and os.path.exists(outro_path):
            self.log_job(job_id, "Standardizing Outro...", "info")
            temp_outro_dir = os.path.join(output_folder_base, "temp_global")
            os.makedirs(temp_outro_dir, exist_ok=True)
            final_outro = os.path.join(temp_outro_dir, "ready_outro.mp4")
            self._normalize_video(outro_path, final_outro)

        for idx, vid_path in enumerate(videos, 1):
            vid_id_str = str(idx) # "1", "2"
            vid_name = os.path.basename(vid_path)

            if vid_id_str not in tasks:
                if len(videos) > 1:
                    self.log_job(job_id, f"⏭️ Skipping {vid_name} (No tasks for ID {vid_id_str})", "warn")
                continue

            segments = tasks[vid_id_str]
            self.log_job(job_id, f"🎬 Processing Video {idx} ({vid_name}) - {len(segments)} segments", "info")

            current_output_folder = os.path.join(output_folder_base, vid_id_str)
            os.makedirs(current_output_folder, exist_ok=True)

            temp_dir = os.path.join(current_output_folder, f"temp_{uuid.uuid4().hex[:4]}")
            os.makedirs(temp_dir, exist_ok=True)

            processed_clips = []

            try:
                total_dur = self._get_duration(vid_path)

                for i, (start, end) in enumerate(segments):
                    if start >= total_dur: continue
                    actual_end = min(end, total_dur)

                    if config.get("smart_cut_mode", True):
                        actual_end = self._smart_adjust(vid_path, start, actual_end, temp_dir, config.get("whisper_model", "small"))

                    dur = actual_end - start
                    if dur <= 1: continue

                    base = f"clip_{i+1}_{uuid.uuid4().hex[:4]}"
                    raw = os.path.join(temp_dir, f"raw_{base}.mp4")
                    work = raw
                    final = os.path.join(temp_dir, f"{base}.mp4")

                    self._cut_video(vid_path, start, dur, raw)

                    if config.get("remove_silence", False):
                        jump = os.path.join(temp_dir, f"jump_{base}.mp4")
                        if self._silence_remove(raw, jump): work = jump

                    ass = None
                    if config.get("add_subtitles", True):
                        try:
                            ass = os.path.join(temp_dir, f"{base}.ass")
                            self._gen_subs(work, ass, config.get("whisper_model", "small"))
                        except: pass

                    self.log_job(job_id, f"   > Rendering Clip {i+1}...", "info")
                    self._ffmpeg_render(
                        work, final,
                        config.get("resize_mode", "podcast_split"),
                        config.get("watermark_text", ""),
                        ass,
                        self._analyze_face_jump(work) if config.get("resize_mode") == "face_jump" else None
                    )

                    if not config.get("merge_clips", False) and final_outro:
                        self.log_job(job_id, "   > Appending Outro...", "info")
                        with_outro = os.path.join(temp_dir, f"outro_{base}.mp4")
                        self._concat_smart([final, final_outro], with_outro)
                        final = with_outro

                    if os.path.exists(final): processed_clips.append(final)

                if config.get("merge_clips", False) and processed_clips:
                    if final_outro: processed_clips.append(final_outro)
                    merged_name = f"FullSequence_{vid_id_str}.mp4"
                    merged_path = os.path.join(current_output_folder, merged_name)
                    self._concat_smart(processed_clips, merged_path)
                    self.log_job(job_id, f"✅ Video {idx} Finished: {merged_name}", "success")
                else:
                    for p in processed_clips:
                        if p == final_outro: continue
                        dst = os.path.join(current_output_folder, os.path.basename(p))
                        if os.path.exists(dst): os.remove(dst)
                        shutil.move(p, dst)
                    self.log_job(job_id, f"✅ Video {idx} Finished: {len(processed_clips)} clips.", "success")

            finally:
                shutil.rmtree(temp_dir, ignore_errors=True)

        if final_outro and os.path.exists(os.path.dirname(final_outro)):
            shutil.rmtree(os.path.dirname(final_outro), ignore_errors=True)

    def _parse_time(self, t):
        try:
            p = t.split(':')
            if len(p)==2: return int(p[0])*60 + int(p[1])
            if len(p)==3: return int(p[0])*3600 + int(p[1])*60 + int(p[2])
        except: return None

    def _get_duration(self, f):
        try:
            res = subprocess.run([self.ffprobe_path, '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', f], capture_output=True, text=True)
            return float(res.stdout.strip())
        except: return 5.0

    def _cut_video(self, inp, start, dur, out):
        subprocess.run([self.ffmpeg_path, '-y', '-ss', str(start), '-i', inp, '-t', str(dur), '-c', 'copy', out], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def _normalize_video(self, inp, out):
        cmd = [
            self.ffmpeg_path, '-y', '-i', inp,
            '-vf', 'scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,setsar=1',
            '-r', '30', '-c:v', 'libx264', '-preset', 'ultrafast',
            '-c:a', 'aac', '-ar', '44100', '-ac', '2',
            out
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def _concat_smart(self, clips, out):
        lst = f"list_{uuid.uuid4().hex}.txt"
        with open(lst, 'w') as f:
            for c in clips: f.write(f"file '{os.path.abspath(c)}'\n")
        cmd_copy = [self.ffmpeg_path, '-y', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', out]
        ret = subprocess.run(cmd_copy, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if ret.returncode != 0:
            cmd_enc = [self.ffmpeg_path, '-y', '-f', 'concat', '-safe', '0', '-i', lst, '-c:v', 'libx264', '-c:a', 'aac', out]
            subprocess.run(cmd_enc, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        os.remove(lst)

    def _smart_adjust(self, inp, start, end, tmp, model_sz):
        try:
            check_dur = (end - start) + 15
            aud = os.path.join(tmp, f"seek_{uuid.uuid4().hex}.mp3")
            subprocess.run([self.ffmpeg_path, '-y', '-ss', str(start), '-i', inp, '-t', str(check_dur), '-vn', '-acodec', 'libmp3lame', '-q:a', '2', aud], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if model_sz not in self.whisper_cache: self.whisper_cache[model_sz] = WhisperModel(model_sz, device="cpu", compute_type="int8")
            segments, _ = self.whisper_cache[model_sz].transcribe(aud, word_timestamps=True)
            target = end - start
            best = end
            min_diff = 999
            for s in segments:
                for w in s.words:
                    if w.word.strip()[-1] in '.!?':
                        diff = abs(w.end - target)
                        if diff < min_diff:
                            min_diff = diff
                            best = start + w.end + 0.2
            os.remove(aud)
            return best
        except: return end

    def _silence_remove(self, inp, out): return False

    def _gen_subs(self, inp, out, model_sz):
        aud = inp.replace(".mp4", ".mp3")
        subprocess.run([self.ffmpeg_path, '-y', '-i', inp, '-vn', '-acodec', 'libmp3lame', aud], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if model_sz not in self.whisper_cache: self.whisper_cache[model_sz] = WhisperModel(model_sz, device="cpu", compute_type="int8")
        segments, _ = self.whisper_cache[model_sz].transcribe(aud, word_timestamps=True)
        header = """[Script Info]\nScriptType: v4.00+\nPlayResX: 1080\nPlayResY: 1920\n[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\nStyle: Default,Arial,65,&H0000FFFF,&H0000FFFF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,3,0,2,135,135,250,1\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"""
        with open(out, "w", encoding="utf-8") as f:
            f.write(header)
            for s in segments:
                for w in s.words:
                    h1,m1,s1,cs1 = self._time_parts(w.start)
                    h2,m2,s2,cs2 = self._time_parts(w.end)
                    k = int((w.end - w.start)*100)
                    f.write(f"Dialogue: 0,{h1}:{m1:02d}:{s1:02d}.{cs1:02d},{h2}:{m2:02d}:{s2:02d}.{cs2:02d},Default,,0,0,0,,{{\\k{k}}}{w.word.strip()}\n")
        if os.path.exists(aud): os.remove(aud)

    def _time_parts(self, s): return int(s//3600), int((s%3600)//60), int(s%60), int((s%1)*100)
    def _analyze_face_jump(self, v): return "(iw-ow)/2"
    def _analyze_mouse_smooth(self, v): return "(iw-ow)/2"

    def _ffmpeg_render(self, inp, out, mode, wm, ass, crop):
        vf = []
        if mode == "podcast_split":
            m = 20
            vf.append(f"[0:v]crop=w=iw-{2*m}:h=ih-{2*m}:x={m}:y={m},split=2[c1][c2]")
            vf.append(f"[c1]crop=w='min(iw, ih*1.125)':h=ih:x=0:y=0[top]")
            vf.append(f"[c2]crop=w='min(iw, ih*1.125)':h=ih:x='iw-ow':y=0[bottom]")
            vf.append(f"[top][bottom]vstack=inputs=2,scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1[bg]")
        else:
            vf.append(f"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1[bg]")

        last = "[bg]"
        if wm:
            clean_wm = wm.replace(":", "\\:").replace("'", "")
            vf.append(f"{last}drawtext=text='{clean_wm}':fontcolor=white:alpha=0.5:fontsize=40:x=(w-text_w)/2:y=h-th-50[wm]")
            last = "[wm]"

        if ass and os.path.exists(ass):
            escaped_ass = ass.replace("\\", "/").replace(":", "\\:")
            vf.append(f"{last}subtitles='{escaped_ass}'[fin]")
            last = "[fin]"

        cmd = [
            self.ffmpeg_path, '-y', '-i', inp,
            '-filter_complex', ";".join(vf),
            '-map', last, '-map', '0:a',
            '-r', '30', '-c:v', 'libx264', '-preset', 'ultrafast', '-c:a', 'aac', '-ar', '44100', '-ac', '2',
            out
        ]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
