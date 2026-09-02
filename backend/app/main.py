from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from backend.app.config import settings
from backend.app.database.session import Base, engine
from backend.app.database.seed_database import seed
from backend.app.api import auth, obras, leitor, chat, checkpoints, admin, llm_config, cientifico

# Criar tabelas e executar seed automático se o banco não existir
Base.metadata.create_all(bind=engine)
try:
    seed()
except Exception as e:
    print(f"[Seed Warning]: {e}")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Plataforma de Mediação Leitora Agêntica com 4 Camadas IAVE, RAG Transparente, Pipeline Gutenberg/Google Books e Motor Multi-LLM."
)

# Configuração de CORS para permitir acesso a partir do frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusão dos Roteadores da API
app.include_router(auth.router, prefix=settings.API_PREFIX)
app.include_router(obras.router, prefix=settings.API_PREFIX)
app.include_router(leitor.router, prefix=settings.API_PREFIX)
app.include_router(chat.router, prefix=settings.API_PREFIX)
app.include_router(checkpoints.router, prefix=settings.API_PREFIX)
app.include_router(admin.router, prefix=settings.API_PREFIX)
app.include_router(llm_config.router, prefix=settings.API_PREFIX)
app.include_router(cientifico.router, prefix=settings.API_PREFIX)

@app.get("/")
def health_check():
    return {
        "status": "online",
        "app": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "mcp_status": "active",
        "multi_llm_status": "active",
        "iave_layers": 4,
        "docs_url": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="127.0.0.1", port=8000, reload=True)
