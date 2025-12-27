REM#######################################################################
REM WEBSITE https://flowork.cloud
REM File NAME : C:\flowork-nano\3-RUN_DOCKER.bat total lines 68 
REM#######################################################################

@echo off
TITLE FLOWORK - Docker Launcher v2.0 (Neural Watchdog Enabled)
cd /d "%~dp0"

cls
echo =================================================================
echo           FLOWORK DOCKER STACK LAUNCHER [NEURAL EDITION]
echo =================================================================
echo.
echo --- [STEP 1/4] Ensuring Docker Desktop is running ---
docker info > nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker Desktop is not running. Please start it.
    pause
    exit /b 1
)
echo [SUCCESS] Docker Desktop is active.

echo.
echo --- [STEP 2/4] Stopping any old running containers ---
docker-compose down
echo [SUCCESS] Old containers stopped.

echo.
echo --- [STEP 2.5] NEURAL WATCHDOG: Cleaning Python Cache ---
REM English: Deleting pycache to prevent 500 Internal Server Errors from stale code
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
echo [SUCCESS] System cleaned. Ready for fresh indexing.

echo.
echo --- [STEP 3/4] Starting services (Volume Mapping Active) ---
docker-compose up -d

if %errorlevel% neq 0 (
    echo [ERROR] Docker Compose failed to start.
    pause
    exit /b 1
)

echo.
echo --- [STEP 4/4] Finalizing Neural Atlas ---
docker-compose ps
echo.
echo [INFO] Waiting for Core Engine to build Neural Index (approx 10s)...
echo ------------------------------------------------------------
echo [INFO] Main GUI: https://flowork.cloud
echo ------------------------------------------------------------

echo.
echo --- [ AUTO-LOG ] FINDING PRIVATE KEY... ---
set "KEY_FILE_PATH=%~dp0\data\DO_NOT_DELETE_private_key.txt"
if exist "%KEY_FILE_PATH%" (
    echo !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    echo !!! YOUR LOGIN PRIVATE KEY IS:
    TYPE "%KEY_FILE_PATH%"
    echo !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
) else (
    echo [ERROR] Finding key in logs...
    docker compose logs gateway | findstr /C:"!!! Generated NEW Private Key:" /C:"0x"
)
echo.
pause
