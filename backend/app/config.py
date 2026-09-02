import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="allow")

    PROJECT_NAME: str = "RELIA - Roteiro de Leitura Empática e Interativa com Agentes"
    VERSION: str = "2.0.0-agentic"
    API_PREFIX: str = "/api"
    
    # Caminhos
    BASE_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    DATA_DIR: str = os.path.join(BASE_DIR, "data")
    DATABASE_URL: str = f"sqlite:///{os.path.join(DATA_DIR, 'relia_local.db')}"
    
    # Segurança e JWT
    SECRET_KEY: str = os.environ.get("SECRET_KEY", "relia-phd-super-secret-key-2026-humanidades-digitais")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 7 dias
    
    # Provedores de LLM
    GEMINI_API_KEY: Optional[str] = os.environ.get("GEMINI_API_KEY", None)
    OPENAI_API_KEY: Optional[str] = os.environ.get("OPENAI_API_KEY", None)
    ANTHROPIC_API_KEY: Optional[str] = os.environ.get("ANTHROPIC_API_KEY", None)
    OLLAMA_BASE_URL: str = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
    DEFAULT_LLM_PROVIDER: str = os.environ.get("DEFAULT_LLM_PROVIDER", "gemini") # gemini | openai | claude | ollama

settings = Settings()
