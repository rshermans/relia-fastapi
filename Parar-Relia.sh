#!/usr/bin/env bash
# Encerrar processos locais do RELIA 2.0
echo "A encerrar servicos locais do RELIA 2.0..."

# Matar processos uvicorn e http.server associados ao projeto
pkill -f "uvicorn backend.app.main:app" 2>/dev/null || true
pkill -f "http.server 3030" 2>/dev/null || true

echo "Servicos locais encerrados com sucesso."
