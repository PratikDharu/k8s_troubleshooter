#!/bin/bash
set -euo pipefail

OLLAMA_MODEL="${OLLAMA_MODEL:-llama3.2:1b}"

if command -v ollama >/dev/null 2>&1; then
  ollama serve > /tmp/ollama.log 2>&1 &

  for _ in $(seq 1 30); do
    if curl -sf http://127.0.0.1:11434/api/tags >/dev/null 2>&1; then
      break
    fi
    sleep 2
  done

  ollama pull "$OLLAMA_MODEL" || true
fi

exec python -m app.container
