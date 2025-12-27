#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\FLOWORK\flowork-gui\scripts\build_engine.py
# JUMLAH BARIS : 149
#######################################################################

import os
import sys
import subprocess
import shutil
import time
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
COMPILATION_MAP = {
    "flowork_kernel/services":                        ".service",
    "scanners":                                       ".scanner.flowork",
    "ai_providers":                                   ".ai",
    "flowork_kernel/kernel_logic.py":                 ".kernel",
    "flowork_kernel/api_contract.py":                 ".kernel",
    "flowork_kernel/core/permission_hook.py":         ".kernel",
    "flowork_kernel/execution/CheckpointManager.py":  ".kernel",
    "flowork_kernel/execution/LoopHandler.py":        ".kernel",
    "flowork_kernel/execution/RetryHandler.py":       ".kernel",
    "flowork_kernel/execution/VariableResolver.py":   ".kernel",
    "flowork_kernel/ui_shell/authentication_dialog.py": ".kernel",
    "flowork_kernel/ui_shell/main_window.py":         ".kernel",
    "flowork_kernel/ui_shell/ui_components/menubar_manager.py": ".kernel",
    "launcher.py":                                    ".flow",
    "pre_launcher.py":                                ".flow"
}
EXCLUDE_LIST = [
    "auto_compiler_service.py",
    "startup_service.py",
    "integrity_checker_service.py",
    "license_manager_service.py",
    os.path.join(PROJECT_ROOT, "scanners", "base_scanner.py"),
    os.path.join(PROJECT_ROOT, "flowork_kernel", "kernel.py"),
    os.path.join(PROJECT_ROOT, "flowork_kernel", "api_client.py"),
    os.path.join(PROJECT_ROOT, "scripts", "build_engine.py"),
    os.path.join(PROJECT_ROOT, "ai_providers", "BaseAIProvider.py")
]
NUITKA_BASE_COMMAND = [
    sys.executable,
    "-m", "nuitka",
    "--module",
    "--remove-output",
    "--windows-console-mode=disable",
    "--lto=yes",
    "--python-flag=-OO",
    "--include-package=scanners"
]
def compile_file(file_path, target_extension):
    """Compiles a single Python file and then deletes the source .py and .pyi files."""
    rel_path = os.path.relpath(file_path, PROJECT_ROOT)
    print(f"  -> Compiling: {rel_path} -> {target_extension}")
    is_launcher_stub = os.path.basename(file_path) in ["launcher.py", "pre_launcher.py"]
    if is_launcher_stub:
        temp_dir = os.path.join(PROJECT_ROOT, "temp_build")
        os.makedirs(temp_dir, exist_ok=True)
        temp_file_path = os.path.join(temp_dir, os.path.basename(file_path))
        shutil.copy2(file_path, temp_file_path)
        path_to_compile = temp_file_path
        output_dir = os.path.dirname(file_path)
    else:
        path_to_compile = file_path
        output_dir = os.path.dirname(file_path)
    command = NUITKA_BASE_COMMAND + [f"--output-dir={output_dir}", path_to_compile]
    try:
        subprocess.run(command, check=True, capture_output=True, text=True, cwd=PROJECT_ROOT, shell=True)
        original_filename_base = os.path.splitext(os.path.basename(path_to_compile))[0]
        compiled_ext = ".pyd" if sys.platform == "win32" else ".so"
        target_file = os.path.join(output_dir, f"{original_filename_base}{target_extension}")
        generated_file = None
        for file in os.listdir(output_dir):
            if file.startswith(original_filename_base) and file.endswith(compiled_ext):
                generated_file = os.path.join(output_dir, file)
                break
        if generated_file and os.path.exists(generated_file):
            if os.path.exists(target_file):
                os.remove(target_file)
            os.rename(generated_file, target_file)
            print(f"  [SUCCESS] Created: {os.path.basename(target_file)}")
            if not is_launcher_stub:
                try:
                    pyi_file = os.path.splitext(file_path)[0] + '.pyi'
                    if os.path.exists(pyi_file):
                        os.remove(pyi_file)
                    os.remove(file_path)
                except OSError as e:
                    print(f"  [WARNING] Could not delete source/stub files for '{rel_path}': {e}")
            return True
        else:
            print(f"  [ERROR] Nuitka did not produce the expected output file for '{rel_path}'")
            return False
    except subprocess.CalledProcessError as e:
        print(f"  [FATAL] Nuitka compilation FAILED for '{rel_path}'.")
        print(f"  --- Nuitka Error Output ---\n{e.stderr}\n  ---------------------------")
        return False
    except Exception as e:
        print(f"  [FATAL] An unexpected error occurred during compilation of '{rel_path}': {e}")
        return False
    finally:
        if 'temp_dir' in locals() and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
def main():
    print("--- Flowork Multi-Target Build Engine (with Source Deletion) ---")
    files_to_compile = []
    absolute_exclude_set = {os.path.abspath(p) for p in EXCLUDE_LIST}
    for path, ext in COMPILATION_MAP.items():
        path_parts = os.path.normpath(path).split(os.sep)
        if 'vendor' in path_parts:
            print(f"  -> INFO: Skipping '{path}' because it is inside a 'vendor' directory.")
            continue # Move to the next item in the compilation map.
        full_path = os.path.join(PROJECT_ROOT, path)
        if os.path.isdir(full_path):
            for root, dirs, files in os.walk(full_path):
                if 'vendor' in dirs:
                    dirs.remove('vendor')
                for file in files:
                    file_abs_path = os.path.abspath(os.path.join(root, file))
                    if file.endswith('.py') and not file.startswith('__') and file_abs_path not in absolute_exclude_set:
                        files_to_compile.append((file_abs_path, ext))
        elif os.path.isfile(full_path):
            if os.path.abspath(full_path) not in absolute_exclude_set:
                files_to_compile.append((full_path, ext))
    if not files_to_compile:
        print("  -> No files found to compile based on the map.")
        return
    success_count = 0
    fail_count = 0
    start_time = time.time()
    print(f"\n[INFO] Found {len(files_to_compile)} files to compile...")
    for file_path, target_ext in sorted(files_to_compile, key=lambda x: x[0]):
        if compile_file(file_path, target_ext):
            success_count += 1
        else:
            fail_count += 1
    end_time = time.time()
    duration = end_time - start_time
    print("\n--- Build Summary ---")
    print(f"  Total time: {duration:.2f} seconds")
    print(f"  Successfully compiled: {success_count} files")
    print(f"  Failed to compile: {fail_count} files")
    if fail_count > 0:
        print("\n[WARNING] Some services failed to compile. The application may be unstable.")
    else:
        print("\n[SUCCESS] All targeted files compiled successfully!")
if __name__ == "__main__":
    main()
