########################################################################
# WEBSITE https://flowork.cloud
# File NAME : C:\FLOWORK\flowork-gui\install_deps.sh total lines 44 
########################################################################

#!/bin/bash

# ######################################################################
# # Skrip ini HANYA untuk menginstal library untuk FLOWORK-GUI
# # dari file requirements.txt di folder ini.
# ######################################################################

echo "[INFO] Starting FLOWORK GUI dependency installation..."
echo

# Otomatis mendeteksi lokasi folder GUI (tempat .sh ini berada)
GUI_ROOT_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"

# Tentukan path ke Python & requirements.txt di dalam folder ini
PYTHON_EXE="$GUI_ROOT_PATH/python/bin/python"
REQUIREMENTS_FILE="$GUI_ROOT_PATH/requirements.txt"

# Validasi path
if [ ! -f "$PYTHON_EXE" ]; then
    echo "[FATAL] Bundled Python not found at: $PYTHON_EXE"
    exit 1
fi

if [ ! -f "$REQUIREMENTS_FILE" ]; then
    echo "[FATAL] requirements.txt not found at: $REQUIREMENTS_FILE"
    exit 1
fi

echo "[INFO] Python and requirements.txt found."
echo "[INFO] Installing libraries for the GUI... please wait."
echo "----------------------------------------------------------------------"

# Jalankan pip install
"$PYTHON_EXE" -m pip install -r "$REQUIREMENTS_FILE"

echo "----------------------------------------------------------------------"
echo "[SUCCESS] GUI dependencies installed successfully."
echo
