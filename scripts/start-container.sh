#!/usr/bin/env bash
set -euo pipefail

export OLLAMA_HOST="${OLLAMA_HOST:-0.0.0.0:11434}"
export OLLAMA_MODEL="${OLLAMA_MODEL:-qwen3:8b}"
export PIPER_MODEL_PATH="${PIPER_MODEL_PATH:-/models/piper/it_IT-paola-medium.onnx}"
export PIPER_MODEL_URL="${PIPER_MODEL_URL:-https://huggingface.co/rhasspy/piper-voices/resolve/main/it/it_IT/paola/medium/it_IT-paola-medium.onnx}"
export PIPER_CONFIG_URL="${PIPER_CONFIG_URL:-https://huggingface.co/rhasspy/piper-voices/resolve/main/it/it_IT/paola/medium/it_IT-paola-medium.onnx.json}"

ollama serve &
OLLAMA_PID="$!"

cleanup() {
  kill "$OLLAMA_PID" 2>/dev/null || true
}
trap cleanup EXIT

until ollama list >/dev/null 2>&1; do
  sleep 1
done

if [ "${POETRYVOICE_PULL_MODEL:-1}" = "1" ]; then
  ollama pull "$OLLAMA_MODEL"
fi

if [ "${POETRYVOICE_PULL_PIPER:-1}" = "1" ] && [ ! -f "$PIPER_MODEL_PATH" ]; then
  mkdir -p "$(dirname "$PIPER_MODEL_PATH")"
  curl -L --fail --output "$PIPER_MODEL_PATH" "$PIPER_MODEL_URL" || true
  curl -L --fail --output "$PIPER_MODEL_PATH.json" "$PIPER_CONFIG_URL" || true
fi

exec poetryvoice web --host 0.0.0.0 --port "${POETRYVOICE_PORT:-8000}"
