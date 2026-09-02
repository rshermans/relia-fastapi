# ──────────────────────────────────────────────
# RELIA 2.0 Agêntico — Dockerfile Multi-stage
# ──────────────────────────────────────────────
FROM python:3.12-slim AS backend

WORKDIR /app

# Dependências de sistema para bcrypt e compilação
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libffi-dev && \
    rm -rf /var/lib/apt/lists/*

# Instalar dependências Python
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copiar código fonte
COPY backend/ ./backend/
COPY mcp_servers/ ./mcp_servers/
COPY data/ ./data/
COPY pytest.ini ./

# Criar __init__.py (garantia de packages)
RUN touch backend/__init__.py \
    backend/app/__init__.py \
    backend/app/api/__init__.py \
    backend/app/agents/__init__.py \
    backend/app/database/__init__.py \
    backend/app/schemas/__init__.py \
    backend/app/services/__init__.py \
    backend/app/skills/__init__.py \
    backend/tests/__init__.py \
    mcp_servers/__init__.py \
    mcp_servers/corpus_server/__init__.py

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import httpx; r = httpx.get('http://localhost:8000/'); exit(0 if r.status_code == 200 else 1)" || exit 1

CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# ──────────────────────────────────────────────
# Frontend — Nginx a servir ficheiros estáticos
# ──────────────────────────────────────────────
FROM nginx:alpine AS frontend

COPY frontend/ /usr/share/nginx/html/
COPY docker/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 3000
