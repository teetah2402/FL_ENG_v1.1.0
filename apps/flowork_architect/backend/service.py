########################################################################
# WEBSITE https://flowork.cloud
# File NAME : C:\flowork-nano\apps\flowork_architect\backend\service.py total lines 443
########################################################################

import os
import json
import time
import threading
import traceback
import csv
import io
import sys
import shutil
import importlib.util
import fnmatch # WAJIB ADA: Untuk pola wildcard (*.log, .env*)

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

def get_parser_loader():
    try:
        from parsers import load_parsers_map
        return load_parsers_map
    except ImportError:
        try:
            from .parsers import load_parsers_map
            return load_parsers_map
        except ImportError:
            try:
                init_path = os.path.join(current_dir, "parsers", "__init__.py")
                spec = importlib.util.spec_from_file_location("parsers", init_path)
                mod = importlib.util.module_from_spec(spec)
                sys.modules["parsers"] = mod
                spec.loader.exec_module(mod)
                return mod.load_parsers_map
            except Exception as e:
                print(f"[Cortex] CRITICAL: Cannot load parsers engine: {e}")
                return lambda: []

try:
    from flowork_kernel.services.base_service import BaseService
except ImportError:
    class BaseService:
        def __init__(self, k, i): self.logger = k

class ArchitectService(BaseService):
    """
    THE CORTEX MANAGER
    Orchestrates scanning, caching, CRUD, and Knowledge Export.
    """

    _SHARED_DATA = {
        "graph": {"nodes": [], "edges": [], "zombie_count": 0},
        "details": {},
        "lookup": {}
    }
    _IS_SYNCING = False

    def __init__(self, kernel, service_id):
        self.name = "Flowork Cortex"
        super().__init__(kernel, service_id)

        if os.path.exists("/master_workspace"):
            self.root_dir = "/master_workspace"
        else:
            self.root_dir = os.getcwd()
            if os.path.exists(os.path.join(os.path.dirname(self.root_dir), "flowork-gateway")):
                self.root_dir = os.path.dirname(self.root_dir)

        self.logger.info(f"[{self.name}] Universe Root: {self.root_dir}")

        loader = get_parser_loader()
        self.parsers = loader()
        self.app_backend = os.path.join(self.root_dir, "apps", "flowork_architect", "backend")
        if not os.path.exists(self.app_backend):
             self.app_backend = os.path.join(os.getcwd(), "apps", "flowork_architect", "backend")
        self.cache_path = os.path.join(self.app_backend, "neural_atlas_cache.json")

    async def start(self):
        self.force_sync()

    def force_sync(self):
        if ArchitectService._IS_SYNCING:
            return {"status": "busy", "message": "Cortex is thinking..."}
        thread = threading.Thread(target=self.build_atlas)
        thread.start()
        return {"status": "success", "message": "Neural Scan Initiated."}

    def build_atlas(self):
        ArchitectService._IS_SYNCING = True
        self.logger.info(f"[{self.name}] Starting Deep Scan (With Smart Filters)...")

        nodes = []
        file_details = {}
        id_counter = 1
        file_map = {}
        filename_map = {}
        lookup = {}

        try:
            IGNORE_PATTERNS = [
                '.git', '.idea', '.vscode', '.github',
                '.venv', 'venv', 'env',
                '__pycache__', '.pytest_cache', '.mypy_cache', '.ruff_cache', '*.egg-info',
                'node_modules', 'dist', 'build', 'vendor',
                'cache', 'llama_tools', 'unsloth_compiled_cache',
                'temp_research_audio', 'llama.cpp', # Folder berat AI
                'backup', 'data', 'logs', '_logs', 'ai_models', # Folder data/logs
                'nodejs','neural_atlas_cache.json',

                '*.pyc', '*.pyo', '*.pyd',
                '*.log', '*.db', '*.sqlite3', 'dump.rdb', # Database & Logs
                '.env*', '*.env', # Config rahasia (opsional, tapi lu minta exclude)
                '.dockerignore', '.gitignore', 'pre_launcher.pid',

                '5-upload_momod_gui.bat',
                '6-upload_flowork_gui.bat',
                '7-upload-docs.bat',
                '8.publish.bat',
                '9.upload_all_project.bat',
                '10.BACKUPENGINE.bat',
                '11.BACKUPGUI.bat'
            ]

            def is_excluded(name):
                for pattern in IGNORE_PATTERNS:
                    if fnmatch.fnmatch(name, pattern):
                        return True
                return False

            for root, dirs, files in os.walk(self.root_dir):
                dirs[:] = [d for d in dirs if not is_excluded(d)]

                for file in files:
                    if is_excluded(file):
                        continue # Skip file ini

                    try: # SAFETY NET PER FILE
                        full_path = os.path.join(root, file)
                        rel_path = os.path.relpath(full_path, self.root_dir).replace("\\", "/")
                        parts = file.split('.')
                        ext = parts[-1].lower() if len(parts) > 1 else file.lower()

                        active_parser = None
                        for parser in self.parsers:
                            if parser.supports(file, ext):
                                active_parser = parser
                                break

                        node_color = "#999999"
                        node_icon = "f15b"
                        analysis = {
                            "imports": [], "assets": [], "structure": [],
                            "metrics": {"loc": 0, "complexity": "LOW", "todo_count": 0},
                            "is_binary": False
                        }
                        content = ""

                        if active_parser:
                            node_color = active_parser.color
                            node_icon = active_parser.icon
                            try:
                                if ext in ['db', 'sqlite', 'db-shm', 'db-wal', 'png', 'jpg', 'jpeg', 'gif', 'zip', 'pdf', 'exe', 'bin', 'safetensors', 'gguf']:
                                    analysis = active_parser.parse(full_path, rel_path)
                                else:
                                    with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                                        content = f.read()
                                    analysis = active_parser.parse(content, rel_path)
                            except Exception as pe:
                                print(f"[Cortex] Parser Error on {file}: {pe}")
                                analysis["structure"] = [{"name": "Parse Error", "type": "error", "icon": "fa-bug"}]
                        else:
                            if ext in ['txt','md','json','yml', 'css', 'js', 'html']:
                                try:
                                    with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                                        content = f.read()
                                        analysis["metrics"]["loc"] = len(content.splitlines())
                                except: pass

                        try: analysis["metrics"]["last_modified"] = os.path.getmtime(full_path)
                        except: analysis["metrics"]["last_modified"] = 0

                        node = {
                            "id": id_counter,
                            "label": file,
                            "title": rel_path,
                            "path": rel_path,
                            "color": node_color,
                            "icon_code": node_icon,
                            "icon_face": "Brands" if ext in ["py", "js", "html", "css", "vue"] else "Free",
                            "group": rel_path.split('/')[0],
                            "ext": ext,
                            "is_zombie": False
                        }
                        nodes.append(node)

                        file_map[rel_path] = node["id"]
                        lookup[node["id"]] = rel_path
                        if file not in filename_map: filename_map[file] = []
                        filename_map[file].append(rel_path)

                        stored_content = content if isinstance(content, str) and len(content) < 100000 else "[LARGE/BINARY FILE]"

                        file_details[rel_path] = {
                            "id": node["id"],
                            "content": stored_content,
                            "structure": analysis.get("structure", []),
                            "metrics": analysis.get("metrics", {}),
                            "raw_imports": list(analysis.get("imports", [])),
                            "raw_assets": list(analysis.get("assets", [])),
                            "inbound_paths": [],
                            "outbound_paths": []
                        }
                        id_counter += 1

                    except Exception as file_e:
                        print(f"[Cortex] CRITICAL SKIP FILE {file}: {file_e}")
                        continue

            self.logger.info(f"[{self.name}] Wiring Nodes ({len(nodes)} files)...")
            edges = []
            unique_edges = set()

            def add_edge(src_path, tgt_path):
                if src_path == tgt_path: return
                if tgt_path not in file_details: return
                s_id = file_details[src_path]["id"]
                t_id = file_details[tgt_path]["id"]
                key = f"{s_id}-{t_id}"
                if key not in unique_edges:
                    if tgt_path not in file_details[src_path]["outbound_paths"]:
                        file_details[src_path]["outbound_paths"].append(tgt_path)
                    if src_path not in file_details[tgt_path]["inbound_paths"]:
                        file_details[tgt_path]["inbound_paths"].append(src_path)
                    edges.append({"from": s_id, "to": t_id, "arrows": "to", "color": {"color": "#666", "opacity": 0.3}})
                    unique_edges.add(key)

            for path, details in file_details.items():
                for imp in details["raw_imports"]:
                    if imp in file_details:
                        add_edge(path, imp)
                        continue
                    target_name = imp.split('/')[-1]
                    candidates = []
                    possible_names = [target_name, f"{target_name}.py", f"{target_name}.js", f"{target_name}.vue", f"{target_name}.html", f"{target_name}.css"]
                    for pname in possible_names:
                        if pname in filename_map: candidates.extend(filename_map[pname])
                    if candidates: add_edge(path, candidates[0])

            zombie_count = 0
            safe_names = ['index.html', 'main.py', 'app.py', 'server.py', 'router.py', 'manage.py', 'start_flowork.py', 'requirements.txt', 'package.json', 'Dockerfile', 'docker-compose.yml']
            for path, details in file_details.items():
                if len(details['inbound_paths']) == 0:
                    is_safe = False
                    fname = path.split('/')[-1].lower()
                    if fname in safe_names: is_safe = True
                    if path.startswith('apps/') or path.startswith('flowork-core/'): is_safe = True
                    if "router" in fname or "service" in fname: is_safe = True
                    if fname.endswith(('.md', '.txt', '.csv', '.sql', '.env')): is_safe = True

                    if not is_safe:
                        for n in nodes:
                            if n['id'] == details['id']:
                                n['is_zombie'] = True
                                n['color'] = '#ff4444'
                                zombie_count += 1

            ArchitectService._SHARED_DATA = {
                "graph": {"nodes": nodes, "edges": edges, "zombie_count": zombie_count},
                "details": file_details,
                "lookup": lookup,
                "ts": time.time()
            }

            with open(self.cache_path, "w") as f:
                json.dump(ArchitectService._SHARED_DATA, f)

            self.logger.info(f"[{self.name}] Scan Success. Saved {len(nodes)} nodes.")

        except Exception as e:
            self.logger.error(f"[{self.name}] GLOBAL SCAN ERROR: {e}")
            traceback.print_exc()
        finally:
            ArchitectService._IS_SYNCING = False

    def run_scan(self):
        if not ArchitectService._SHARED_DATA["graph"]["nodes"]:
            if os.path.exists(self.cache_path):
                try:
                    with open(self.cache_path, "r") as f:
                        data = json.load(f)
                        ArchitectService._SHARED_DATA = data
                except: self.force_sync()
            else: self.force_sync()
        return ArchitectService._SHARED_DATA["graph"]

    def get_file_intel(self, path, all_nodes_dummy=None):
        if not path: return {"status": "error"}
        details = ArchitectService._SHARED_DATA["details"].get(path)
        if details:
            inbound_nodes = []
            for p in details["inbound_paths"]:
                if p in ArchitectService._SHARED_DATA["details"]:
                    nid = ArchitectService._SHARED_DATA["details"][p]["id"]
                    node = next((n for n in ArchitectService._SHARED_DATA["graph"]["nodes"] if n["id"] == nid), None)
                    if node: inbound_nodes.append(node)
            outbound_nodes = []
            for p in details["outbound_paths"]:
                if p in ArchitectService._SHARED_DATA["details"]:
                    nid = ArchitectService._SHARED_DATA["details"][p]["id"]
                    node = next((n for n in ArchitectService._SHARED_DATA["graph"]["nodes"] if n["id"] == nid), None)
                    if node: outbound_nodes.append(node)
            return {
                "status": "success", "path": path,
                "content": details["content"], "structure": details["structure"],
                "metrics": details["metrics"], "dependencies": details.get("raw_assets", []),
                "inbound": inbound_nodes, "outbound": outbound_nodes
            }
        return {"status": "error", "message": "File chunk not found."}

    def save_file(self, path, content):
        if not path: return {"status": "error"}
        full_path = os.path.join(self.root_dir, path)
        try:
            with open(full_path, "w", encoding="utf-8") as f: f.write(content)
            if path in ArchitectService._SHARED_DATA["details"]:
                ArchitectService._SHARED_DATA["details"][path]["content"] = content
            return {"status": "success"}
        except Exception as e: return {"status": "error", "message": str(e)}

    def export_atlas(self):
        """
        Legacy Knowledge Export (Excel Friendly).
        """
        si = io.StringIO()
        si.write('\ufeff') # BOM for Excel
        cw = csv.writer(si, quoting=csv.QUOTE_ALL)

        cw.writerow(["FILE_PATH", "TYPE", "INBOUND (CALLED_BY)", "OUTBOUND (CALLS_TO)", "DEPENDENCIES", "STRUCTURE"])

        nodes = ArchitectService._SHARED_DATA["graph"]["nodes"]
        details = ArchitectService._SHARED_DATA["details"]

        for node in nodes:
            path = node["path"]
            detail = details.get(path, {})
            ext = node.get("ext", "").upper()

            inbounds = [p.split('/')[-1] for p in detail.get("inbound_paths", [])]
            inbound_str = " | ".join(inbounds) if inbounds else "-"

            outbounds = [p.split('/')[-1] for p in detail.get("outbound_paths", [])]
            outbound_str = " | ".join(outbounds) if outbounds else "-"

            deps = detail.get("raw_assets", [])
            deps_str = " | ".join(deps) if deps else "-"

            struct_list = []
            for item in detail.get("structure", []):
                name = item.get("name", "")
                type_obj = item.get("type", "")
                struct_list.append(f"{type_obj}: {name}")

            struct_str = " | ".join(struct_list) if struct_list else "-"

            cw.writerow([path, ext, inbound_str, outbound_str, deps_str, struct_str])

        return {"status": "success", "csv": si.getvalue()}

    def export_json_atlas(self):
        """
        Export Knowledge Graph as structured JSON for AI Context.
        """
        nodes = ArchitectService._SHARED_DATA["graph"]["nodes"]
        details = ArchitectService._SHARED_DATA["details"]

        data_export = []

        for node in nodes:
            path = node["path"]
            detail = details.get(path, {})

            item = {
                "file_path": path,
                "type": node.get("ext", "").upper(),
                "inbound": [p.split('/')[-1] for p in detail.get("inbound_paths", [])],
                "outbound": [p.split('/')[-1] for p in detail.get("outbound_paths", [])],
                "dependencies": detail.get("raw_assets", []),
                "structure": []
            }

            for s in detail.get("structure", []):
                name = s.get("name", "")
                type_obj = s.get("type", "")
                item["structure"].append(f"{type_obj}: {name}")

            data_export.append(item)

        return {"status": "success", "json": json.dumps(data_export, indent=2)}

    def handle_crud(self, payload):
        action = payload.get('action')
        path = payload.get('path')
        try:
            if action == 'create_file':
                target_dir = payload.get('target_dir', '')
                name = payload.get('name')
                full_dir = os.path.join(self.root_dir, target_dir) if target_dir else self.root_dir
                full_path = os.path.join(full_dir, name)
                if os.path.exists(full_path): return {"status": "error", "message": "File exists"}
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                with open(full_path, 'w', encoding='utf-8') as f: f.write("")
                threading.Thread(target=self.build_atlas).start()
                return {"status": "success", "path": os.path.relpath(full_path, self.root_dir).replace("\\", "/")}
            elif action == 'create_folder':
                target_dir = payload.get('target_dir', '')
                name = payload.get('name')
                full_dir = os.path.join(self.root_dir, target_dir) if target_dir else self.root_dir
                full_path = os.path.join(full_dir, name)
                if os.path.exists(full_path): return {"status": "error", "message": "Folder exists"}
                os.makedirs(full_path)
                threading.Thread(target=self.build_atlas).start()
                return {"status": "success"}
            elif action == 'rename':
                new_name = payload.get('new_name')
                old_path = os.path.join(self.root_dir, path)
                new_path = os.path.join(os.path.dirname(old_path), new_name)
                os.rename(old_path, new_path)
                threading.Thread(target=self.build_atlas).start()
                return {"status": "success"}
            elif action == 'delete':
                full_path = os.path.join(self.root_dir, path)
                if os.path.isdir(full_path): shutil.rmtree(full_path)
                else: os.remove(full_path)
                if path in ArchitectService._SHARED_DATA["details"]:
                    del ArchitectService._SHARED_DATA["details"][path]
                threading.Thread(target=self.build_atlas).start()
                return {"status": "success"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
