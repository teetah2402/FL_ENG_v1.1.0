########################################################################
# WEBSITE https://flowork.cloud
# File NAME : C:\FLOWORK\flowork-gateway\entrypoint.sh total lines 20 
########################################################################

#!/bin/bash
set -e
export PYTHONPATH=/app/app:/app
echo "[BOOT] PYTHONPATH set to: $PYTHONPATH"
: "${DATABASE_URL:=sqlite://///app/data/gateway.db}"
export DATABASE_URL
echo "[BOOT] Using data dir: /app/data"
mkdir -p /app/data/logs /app/data/keys
echo "[BOOT] Applying database migrations (flask db upgrade)..."
flask db upgrade || { echo "[BOOT][FATAL] Database migration failed. Stopping container."; exit 1; }
echo "[BOOT] Creating default admin user (and seeding engine)..."
python /app/create_admin.py || { echo "[BOOT][FATAL] Admin creation failed. Stopping container."; exit 1; }
echo "[BOOT] Starting Gunicorn server (worker-class: gevent)..."
exec gunicorn --bind 0.0.0.0:8000 --workers 2 --worker-class gevent -m 007 "run_gateway:application"
