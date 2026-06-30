FROM nvidia/cuda:12.6.3-cudnn-runtime-ubuntu24.04

ARG INSTALL_HEAVY_TTS=1

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    NVIDIA_VISIBLE_DEVICES=all \
    NVIDIA_DRIVER_CAPABILITIES=compute,utility

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
      ffmpeg \
      curl \
      espeak-ng \
      git \
      python3.12 \
      python3.12-dev \
      python3-pip \
      python3-venv \
      zstd \
    && rm -rf /var/lib/apt/lists/*

RUN python3.12 -m venv /opt/venv
ENV PATH="/opt/venv/bin:${PATH}"

RUN curl -fsSL https://ollama.com/install.sh | sh

COPY pyproject.toml README.md ./
COPY poetry_voice ./poetry_voice
COPY config.example.yaml ./config.yaml
COPY scripts/start-container.sh /usr/local/bin/start-container.sh

RUN pip install --upgrade pip \
    && pip install "." \
    && (pip install ".[piper]" || true) \
    && if [ "$INSTALL_HEAVY_TTS" = "1" ]; then \
         (pip install ".[kokoro]" || true); \
         (pip install ".[xtts]" || true); \
       fi \
    && chmod +x /usr/local/bin/start-container.sh

EXPOSE 8000 11434

CMD ["start-container.sh"]
