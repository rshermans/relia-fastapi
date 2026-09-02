"""
Serviço Unificado de Roteamento e Execução de Modelos de Linguagem (LLMs)
Integra com o UniversalLLMAdapter para suporte nativo a:
Gemini, Claude, OpenAI, DeepSeek, Perplexity, xAI/Grok, Kimi, Qwen e Ollama.
"""

from typing import Dict, Any, List, Optional
from backend.app.services.llm_adapter import llm_adapter

class LLMService:
    async def gerar_resposta_socratica(
        self,
        prompt_sistema: str,
        mensagens_historico: List[Dict[str, str]],
        contexto_corpus: Optional[str] = None,
        nivel_bloom: str = "Entender",
        camada_iave: str = "Camada 2: Análise Retórico-Estilística",
        provider: Optional[str] = None,
        model: Optional[str] = None,
        api_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executa a inferência socrática com ancoragem textual e empática.
        """
        return await llm_adapter.execute_socratic_inference(
            system_prompt=prompt_sistema,
            messages=mensagens_historico,
            context=contexto_corpus,
            provider=provider,
            model=model,
            api_key=api_key,
            bloom_level=nivel_bloom,
            camada_iave=camada_iave
        )

llm_service = LLMService()
