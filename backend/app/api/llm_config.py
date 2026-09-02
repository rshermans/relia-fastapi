"""
Rotas para Configuração e Gestão Dinâmica de Provedores Multi-LLM e Chaves de API
Permite que o utilizador/investigador selecione modelos e configure chaves de forma segura.
"""

from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from backend.app.services.llm_adapter import DEFAULT_MODELS, OPENAI_COMPATIBLE_ENDPOINTS
from backend.app.config import settings

router = APIRouter(prefix="/llm", tags=["Configuração Multi-LLM"])

class LLMProviderInfo(BaseModel):
    id: str
    nome: str
    descricao: str
    modelos_recomendados: List[str]
    modelo_ativo: str
    requer_chave: bool
    chave_configurada: bool

class LLMKeyUpdate(BaseModel):
    provider: str
    api_key: str
    default_model: Optional[str] = None

# Cache em memória para chaves da sessão
SESSION_API_KEYS: Dict[str, str] = {}
SESSION_ACTIVE_MODELS: Dict[str, str] = {}

@router.get("/providers", response_model=List[LLMProviderInfo])
def listar_provedores_disponiveis():
    """
    Retorna todos os provedores suportados pelo RELIA 2.0 e seus status de configuração.
    """
    providers_catalog = [
        {
            "id": "gemini",
            "nome": "Google Gemini",
            "descricao": "Janela de contexto ultra-longa (1M-2M tokens) e excelente raciocínio multimodal.",
            "modelos_recomendados": ["gemini-1.5-pro-latest", "gemini-1.5-flash-latest", "gemini-2.0-flash"],
            "requer_chave": True,
            "chave_configurada": bool(SESSION_API_KEYS.get("gemini") or settings.GEMINI_API_KEY)
        },
        {
            "id": "claude",
            "nome": "Anthropic Claude",
            "descricao": "Altíssima sofisticação estilística e hermenêutica em Língua Portuguesa formal.",
            "modelos_recomendados": ["claude-3-5-sonnet-20241022", "claude-3-5-haiku-20241022"],
            "requer_chave": True,
            "chave_configurada": bool(SESSION_API_KEYS.get("claude") or settings.ANTHROPIC_API_KEY)
        },
        {
            "id": "openai",
            "nome": "OpenAI (GPT-4o)",
            "descricao": "Raciocínio lógico estruturado e precisão na geração de JSON Schemas.",
            "modelos_recomendados": ["gpt-4o", "gpt-4o-mini", "o1-preview"],
            "requer_chave": True,
            "chave_configurada": bool(SESSION_API_KEYS.get("openai") or settings.OPENAI_API_KEY)
        },
        {
            "id": "deepseek",
            "nome": "DeepSeek",
            "descricao": "Modelo de raciocínio profundo de alto desempenho e excelente custo-benefício.",
            "modelos_recomendados": ["deepseek-chat", "deepseek-reasoner"],
            "requer_chave": True,
            "chave_configurada": bool(SESSION_API_KEYS.get("deepseek"))
        },
        {
            "id": "perplexity",
            "nome": "Perplexity AI",
            "descricao": "Ancoragem factológica e pesquisa de referências filológicas externas.",
            "modelos_recomendados": ["sonar-pro", "sonar"],
            "requer_chave": True,
            "chave_configurada": bool(SESSION_API_KEYS.get("perplexity"))
        },
        {
            "id": "xai",
            "nome": "xAI (Grok)",
            "descricao": "Exploração crítica sem amarras e discussões interpretativas complexas.",
            "modelos_recomendados": ["grok-beta", "grok-2"],
            "requer_chave": True,
            "chave_configurada": bool(SESSION_API_KEYS.get("xai"))
        },
        {
            "id": "kimi",
            "nome": "Moonshot AI (Kimi)",
            "descricao": "Processamento de contexto estendido para romances e sermões volumosos.",
            "modelos_recomendados": ["moonshot-v1-32k", "moonshot-v1-128k"],
            "requer_chave": True,
            "chave_configurada": bool(SESSION_API_KEYS.get("kimi"))
        },
        {
            "id": "qwen",
            "nome": "Alibaba Qwen",
            "descricao": "Excelente capacidade multilíngue e análise semântica avançada.",
            "modelos_recomendados": ["qwen-plus", "qwen-max", "qwen-turbo"],
            "requer_chave": True,
            "chave_configurada": bool(SESSION_API_KEYS.get("qwen"))
        },
        {
            "id": "ollama",
            "nome": "Ollama Local (Offline / RGPD)",
            "descricao": "Execução 100% local e soberana em servidor próprio sem envio de dados externos.",
            "modelos_recomendados": ["llama3.1", "mistral", "gemma2"],
            "requer_chave": False,
            "chave_configurada": True
        }
    ]

    result = []
    for p in providers_catalog:
        p_id = p["id"]
        ativo = SESSION_ACTIVE_MODELS.get(p_id, DEFAULT_MODELS.get(p_id, p["modelos_recomendados"][0]))
        result.append(LLMProviderInfo(
            id=p_id,
            nome=p["nome"],
            descricao=p["descricao"],
            modelos_recomendados=p["modelos_recomendados"],
            modelo_ativo=ativo,
            requer_chave=p["requer_chave"],
            chave_configurada=p["chave_configurada"]
        ))
    return result

@router.post("/set-key")
def salvar_chave_api(payload: LLMKeyUpdate):
    """
    Armazena temporariamente ou atualiza a chave de API e modelo preferido para a sessão.
    """
    provider = payload.provider.lower()
    SESSION_API_KEYS[provider] = payload.api_key.strip()
    if payload.default_model:
        SESSION_ACTIVE_MODELS[provider] = payload.default_model.strip()
    
    return {
        "status": "success",
        "provider": provider,
        "message": f"Chave de API para '{provider}' configurada com sucesso.",
        "model_selected": SESSION_ACTIVE_MODELS.get(provider, DEFAULT_MODELS.get(provider))
    }
