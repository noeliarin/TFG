#!/bin/bash
echo "=== INICIANDO SERVIDOR PYFLUE CON NGROK ==="
read -p "Pega aquí la URL de Ngrok (ej: https://abcd.ngrok.io): " NGROK_URL

export OLLAMA_HOST="$NGROK_URL"
export OLLAMA_BASE_URL="${NGROK_URL}/v1"
export OPENAI_BASE_URL="${NGROK_URL}/v1"

echo "Variables configuradas:"
echo "OLLAMA_HOST = $OLLAMA_HOST"
echo "OLLAMA_BASE_URL = $OLLAMA_BASE_URL"

echo "Arrancando pyflue dev..."
pyflue dev
