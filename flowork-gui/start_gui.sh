########################################################################
# WEBSITE https://flowork.cloud
# File NAME : C:\FLOWORK\flowork-gui\start_gui.sh total lines 30 
########################################################################

#!/bin/bash
echo "[INFO] Starting FLOWORK GUI..."

# Otomatis mendeteksi lokasi folder GUI
GUI_ROOT_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"

# Tentukan path ke Python & pre-launcher
PYTHON_EXE="$GUI_ROOT_PATH/python/bin/python"
PRE_LAUNCHER_SCRIPT="$GUI_ROOT_PATH/template/default/pre_launcher.py"

# Validasi
if [ ! -f "$PYTHON_EXE" ]; then
    echo "[FATAL] Bundled Python not found at: $PYTHON_EXE"
    exit 1
fi
if [ ! -f "$PRE_LAUNCHER_SCRIPT" ]; then
    echo "[FATAL] Pre-launcher script not found at: $PRE_LAUNCHER_SCRIPT"
    exit 1
fi

echo "[INFO] Launching the preloader..."

# Jalankan pre-launcher di background
"$PYTHON_EXE" "$PRE_LAUNCHER_SCRIPT" &
