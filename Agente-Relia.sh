#!/usr/bin/env bash
# ──────────────────────────────────────────────────────
# RELIA 2.0 Agêntico — Script de Lançamento Linux/macOS
# ──────────────────────────────────────────────────────
set -e

GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${CYAN}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║         RELIA 2.0 — Roteiro de Leitura Empática            ║"
echo "║         e Interativa com Agentes (PhD CEHUM/UMinho)        ║"
echo "╠══════════════════════════════════════════════════════════════╣"
echo "║  Backend:  FastAPI + SQLAlchemy     → http://localhost:8000 ║"
echo "║  Frontend: HTML/CSS/JS             → http://localhost:3000 ║"
echo "║  Swagger:  Documentação da API     → http://localhost:8000/docs ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# ── 1. Verificar Python ──
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}[ERRO] Python 3 não encontrado. Instale Python 3.10+${NC}"
    exit 1
fi
echo -e "${GREEN}[INFO] $(python3 --version) detectado.${NC}"

# ── 2. Criar/Activar virtualenv ──
VENV_DIR="relia-env"
if [ ! -d "$VENV_DIR" ]; then
    echo -e "${YELLOW}[INFO] A criar ambiente virtual '$VENV_DIR'...${NC}"
    python3 -m venv "$VENV_DIR"
fi

source "$VENV_DIR/bin/activate"
echo -e "${GREEN}[INFO] Ambiente virtual activado.${NC}"

# ── 3. Instalar dependências ──
echo -e "${YELLOW}[INFO] A instalar dependências...${NC}"
pip install -q -r backend/requirements.txt

# ── 4. Executar testes (opcional) ──
read -p "Deseja executar os testes antes de iniciar? (S/N): " RUNTESTS
if [[ "$RUNTESTS" =~ ^[Ss]$ ]]; then
    echo -e "${CYAN}[INFO] A executar testes...${NC}"
    python -m pytest backend/tests/ -v --tb=short || {
        echo -e "${YELLOW}[AVISO] Alguns testes falharam.${NC}"
        read -p "Continuar mesmo assim? (S/N): " CONTINUAR
        if [[ ! "$CONTINUAR" =~ ^[Ss]$ ]]; then
            echo "A encerrar."
            exit 1
        fi
    }
fi

# ── 5. Iniciar Backend ──
echo -e "${GREEN}[INFO] A iniciar FastAPI backend na porta 8000...${NC}"
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload &
BACKEND_PID=$!

sleep 3

# ── 6. Iniciar Frontend ──
echo -e "${GREEN}[INFO] A iniciar frontend na porta 3030...${NC}"
cd frontend && python3 -m http.server 3030 &
FRONTEND_PID=$!
cd "$SCRIPT_DIR"

sleep 1

echo ""
echo -e "${CYAN}══════════════════════════════════════════════════════════════${NC}"
echo -e "  ${GREEN}RELIA 2.0 está a correr!${NC}"
echo ""
echo "  Frontend:  http://localhost:3030"
echo "  API Docs:  http://localhost:8000/docs"
echo "  Health:    http://localhost:8000/"
echo ""
echo "  Para parar: Ctrl+C"
echo -e "${CYAN}══════════════════════════════════════════════════════════════${NC}"
echo ""

# Abrir browser
if command -v xdg-open &> /dev/null; then
    xdg-open http://localhost:3030
elif command -v open &> /dev/null; then
    open http://localhost:3030
fi

# ── 7. Cleanup no Ctrl+C ──
cleanup() {
    echo ""
    echo -e "${YELLOW}[INFO] A encerrar serviços...${NC}"
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo -e "${GREEN}[INFO] Todos os serviços foram encerrados.${NC}"
    exit 0
}

trap cleanup SIGINT SIGTERM

# Manter vivo
wait
