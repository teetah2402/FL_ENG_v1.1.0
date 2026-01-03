#######################################################################
# WEBSITE https://flowork.cloud
# File NAME : flowork-core/Dockerfile
# AUTHOR : flowork dev
# VERSION : 5.1 (IMMORTAL CORE - Zero Maintenance Ready)
# REFACTORED BY GEMINI - RULE 2: Decoupled Heavy AI for App-Centric Architecture
#######################################################################

# --- Stage 1: The Builder (Keeping Compilers for Dynamic App Installs) ---
FROM nvidia/cuda:12.4.1-devel-ubuntu22.04 AS builder

ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /app

# 1. Install Python 3.11 & System Dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    software-properties-common \
    curl \
    git \
    build-essential \
    cmake \
    ffmpeg \
    portaudio19-dev \
    libportaudio2 \
    pkg-config \
    libavcodec-dev \
    libavformat-dev \
    libavutil-dev \
    libswscale-dev \
    libavfilter-dev \
    libavdevice-dev \
    && add-apt-repository ppa:deadsnakes/ppa \
    && apt-get update && apt-get install -y \
    python3.11 \
    python3.11-venv \
    python3.11-dev \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# 2. Setup Python Environment
RUN python3.11 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# 4. Install Skeleton Requirements (The lightweight core libs)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade packaging ninja && \
    pip install --no-cache-dir --no-build-isolation -r requirements.txt

# --- Stage 2: The Runner (Optimized for Skeleton Execution & The Mason) ---
FROM nvidia/cuda:12.4.1-runtime-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /app

# Install Runtime Deps & Zero Maintenance Tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    software-properties-common \
    build-essential \
    git \
    ffmpeg \
    libportaudio2 \
    libgomp1 \
    libgl1 \
    libcurl4-openssl-dev \
    curl \
    # --- ADDED: Essential Libraries for Apps (OpenCV, etc) ---
    libsm6 \
    libxext6 \
    libxrender-dev \
    ca-certificates \
    # ---------------------------------------------------------
    # --- [ZERO MAINTENANCE ADDITIONS] ---
    # procps: Wajib untuk 'Ghost Protocol' (command 'ps' untuk cek PID App)
    # unzip & wget: Wajib untuk 'The Teleporter' (Marketplace/Installer)
    # nano: Opsional, berguna untuk debug config mendadak di dalam container
    procps \
    unzip \
    wget \
    nano \
    # ------------------------------------
    && add-apt-repository ppa:deadsnakes/ppa \
    && apt-get update && apt-get install -y \
    python3.11 \
    python3.11-venv \
    python3.11-dev \
    # --- ADDED: Pip in Runner for Dynamic App Installs (Auto-Heal) ---
    python3-pip \
    # -----------------------------------------------------
    && rm -rf /var/lib/apt/lists/*

# --- ADDED: Install Node.js (Required by yt-dlp for JS Runtime) ---
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*
# ------------------------------------------------------------------

# Copy Virtual Env from Builder
COPY --from=builder /opt/venv /opt/venv

# [English Note] Global path management prioritizing our sanitized venv
ENV PATH="/opt/venv/bin:$PATH"
ENV VIRTUAL_ENV="/opt/venv"

# [CACHE BUSTER]
ENV FORCE_CODE_UPDATE=v5.1_IMMORTAL_CORE_ARCHITECTURE

# [ZERO MAINTENANCE OPTIMIZATION]
# Menentukan lokasi cache pip ke volume persisten (/app/data).
# Agar saat Auto-Heal berjalan, dia tidak perlu download ulang library yang sama.
ENV PIP_CACHE_DIR=/app/data/.pip_cache

# [English Note] Creating persistent volumes for Apps and Data
# ensure apps_storage exists for 'The Vault' (Config Injection)
RUN mkdir -p /app/app /app/data /app/logs /app/data/apps_storage

# [English Note] Only install essential conduits for Skeleton operation
RUN /opt/venv/bin/pip install --no-cache-dir numpy

COPY . .

# Environment Variables for GPU acceleration support in Apps
ENV LD_LIBRARY_PATH="/usr/local/cuda/lib64:${LD_LIBRARY_PATH}"
ENV NVIDIA_VISIBLE_DEVICES=all
ENV NVIDIA_DRIVER_CAPABILITIES=compute,utility

# Flowork Core API and Local Dashboard Ports
EXPOSE 8989
EXPOSE 5001

# [English Note] Skeleton Core Conductor Entry point
# Menggunakan run_server.py sesuai file original
CMD ["python", "run_server.py"]