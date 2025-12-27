#######################################################################
# WEBSITE https://flowork.cloud
# File NAME : flowork-core/Dockerfile
# AUTHOR : flowork dev
# VERSION : 5.0 (LITE EDITION - NO GPU REQUIRED)
# ARCH : Multi-arch (Supports AMD64 & ARM64/Raspberry Pi)
#######################################################################

# --- Stage 1: The Builder (Lightweight Python Slim) ---
FROM python:3.11-slim-bookworm AS builder

ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /app

# 1. Install Build Tools & System Dependencies
# Kita butuh build-essential & gcc buat compile library system kayak psutil/cryptography
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    git \
    libffi-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# 2. Setup Python Environment (VENV)
RUN python -m venv /opt/venv
# Prioritize Venv PATH
ENV PATH="/opt/venv/bin:$PATH"

# 3. Upgrade Pip & Build Tools
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# 4. Install Requirements (LITE MODE)
# Hanya install yang ada di requirements.txt baru (System, Network, Server)
COPY requirements.txt .
RUN pip install --no-cache-dir --no-build-isolation -r requirements.txt

# --- Stage 2: The Runner (Final Image) ---
FROM python:3.11-slim-bookworm

ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /app

# 1. Install Runtime Dependencies
# ffmpeg: tetep kita simpan buat jaga-jaga kalau ada audio processing ringan
# curl: buat healthcheck
# git: buat update/clone modul
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# 2. Copy Virtual Env from Builder
COPY --from=builder /opt/venv /opt/venv

# [FIX] Robust Path Management
# Pastikan Python otomatis pakai yang ada di /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
ENV VIRTUAL_ENV="/opt/venv"

# [CACHE BUSTER]
ENV FORCE_CODE_UPDATE=v5.0_LITE_EDGE_EDITION

# 3. Copy Source Code
COPY . .

# 4. Ports
EXPOSE 8989
EXPOSE 5001

# 5. Start Command
CMD ["python", "run_server.py"]