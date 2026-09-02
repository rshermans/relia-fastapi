"""
Adaptador Universal Multi-LLM para o RELIA 2.0
Suporta nativamente e via interfaces compatíveis:
- Google Gemini (Gemini 1.5 Pro / Flash, Gemini 2.0)
- Anthropic Claude (Claude 3.5 Sonnet / Haiku / Opus)
- OpenAI (GPT-4o, GPT-4o-mini, o1)
- DeepSeek (deepseek-chat V3, deepseek-reasoner R1)
- Perplexity AI (sonar, sonar-pro)
- xAI (grok-beta, grok-2)
- Moonshot AI / Kimi (moonshot-v1-8k/32k/128k)
- Alibaba Qwen (qwen-plus, qwen-max, qwen-turbo)
- Ollama Local (llama3.1, mistral, gemma2, etc.)
- Fallback Hermenêutico Estruturado Local
"""

import httpx
from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod
from backend.app.config import settings

# Endpoints padrão de provedores compatíveis com a especificação OpenAI
OPENAI_COMPATIBLE_ENDPOINTS = {
    "openai": "https://api.openai.com/v1",
    "deepseek": "https://api.deepseek.com",
    "perplexity": "https://api.perplexity.ai",
    "xai": "https://api.x.ai/v1",
    "kimi": "https://api.moonshot.cn/v1",
    "moonshot": "https://api.moonshot.cn/v1",
    "qwen": "https://dashscope.aliyuncs.com/compatible-mode/v1",
}

DEFAULT_MODELS = {
    "gemini": "gemini-1.5-pro-latest",
    "claude": "claude-3-5-sonnet-20241022",
    "anthropic": "claude-3-5-sonnet-20241022",
    "openai": "gpt-4o",
    "deepseek": "deepseek-chat",
    "perplexity": "sonar-pro",
    "xai": "grok-beta",
    "kimi": "moonshot-v1-32k",
    "moonshot": "moonshot-v1-32k",
    "qwen": "qwen-plus",
    "ollama": "llama3.1",
}

class BaseLLMProvider(ABC):
    @abstractmethod
    async def generate(
        self,
        system_prompt: str,
        messages: List[Dict[str, str]],
        context: Optional[str] = None,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        temperature: float = 0.7
    ) -> str:
        pass


class GeminiProvider(BaseLLMProvider):
    async def generate(
        self,
        system_prompt: str,
        messages: List[Dict[str, str]],
        context: Optional[str] = None,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        temperature: float = 0.7
    ) -> str:
        key = api_key or settings.GEMINI_API_KEY
        if not key:
            raise ValueError("Chave de API do Google Gemini não configurada.")
        
        model_name = model or DEFAULT_MODELS["gemini"]
        
        # Tentativa via SDK oficial
        try:
            import google.generativeai as genai
            genai.configure(api_key=key)
            gen_model = genai.GenerativeModel(
                model_name,
                generation_config={"temperature": temperature}
            )
            full_prompt = f"{system_prompt}\n\n"
            if context:
                full_prompt += f"Contexto Textual / Excerto:\n{context}\n\n"
            full_prompt += "Histórico da Sessão:\n"
            for m in messages:
                full_prompt += f"{m.get('role', 'user')}: {m.get('content', '')}\n"
            
            resp = gen_model.generate_content(full_prompt)
            if resp and resp.text:
                return resp.text
        except ImportError:
            # Fallback para REST API v1beta caso SDK não esteja disponível
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={key}"
            contents = []
            if system_prompt or context:
                contents.append({
                    "role": "user",
                    "parts": [{"text": f"Instruções do Sistema:\n{system_prompt}\n\nContexto:\n{context or ''}"}]
                })
            for m in messages:
                role = "user" if m.get("role") in ["user", "system"] else "model"
                contents.append({
                    "role": role,
                    "parts": [{"text": m.get("content", "")}]
                })
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                res = await client.post(url, json={"contents": contents, "generationConfig": {"temperature": temperature}})
                res.raise_for_status()
                data = res.json()
                return data["candidates"][0]["content"]["parts"][0]["text"]


class ClaudeProvider(BaseLLMProvider):
    async def generate(
        self,
        system_prompt: str,
        messages: List[Dict[str, str]],
        context: Optional[str] = None,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        temperature: float = 0.7
    ) -> str:
        key = api_key or settings.ANTHROPIC_API_KEY
        if not key:
            raise ValueError("Chave de API do Anthropic Claude não configurada.")
        
        model_name = model or DEFAULT_MODELS["claude"]
        system_text = system_prompt
        if context:
            system_text += f"\n\nContexto do Excerto Literário:\n{context}"
        
        formatted_messages = []
        for m in messages:
            role = m.get("role", "user")
            if role == "system":
                continue
            formatted_messages.append({
                "role": "assistant" if role == "assistant" else "user",
                "content": m.get("content", "")
            })
        
        if not formatted_messages:
            formatted_messages.append({"role": "user", "content": "Por favor, inicie a mediação leitora."})

        async with httpx.AsyncClient(timeout=40.0) as client:
            headers = {
                "x-api-key": key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            }
            payload = {
                "model": model_name,
                "max_tokens": 2048,
                "temperature": temperature,
                "system": system_text,
                "messages": formatted_messages
            }
            resp = await client.post("https://api.anthropic.com/v1/messages", headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            return data["content"][0]["text"]


class OpenAICompatibleProvider(BaseLLMProvider):
    def __init__(self, provider_name: str, custom_base_url: Optional[str] = None):
        self.provider_name = provider_name.lower()
        self.base_url = custom_base_url or OPENAI_COMPATIBLE_ENDPOINTS.get(self.provider_name, "https://api.openai.com/v1")

    async def generate(
        self,
        system_prompt: str,
        messages: List[Dict[str, str]],
        context: Optional[str] = None,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        temperature: float = 0.7
    ) -> str:
        key = api_key or getattr(settings, f"{self.provider_name.upper()}_API_KEY", None) or settings.OPENAI_API_KEY
        if not key and self.provider_name not in ["ollama"]:
            raise ValueError(f"Chave de API para {self.provider_name} não encontrada.")
        
        model_name = model or DEFAULT_MODELS.get(self.provider_name, "gpt-4o")
        
        system_content = system_prompt
        if context:
            system_content += f"\n\nContexto Literário / Excerto:\n{context}"
        
        formatted_messages = [{"role": "system", "content": system_content}]
        for m in messages:
            if m.get("role") != "system":
                formatted_messages.append({"role": m.get("role", "user"), "content": m.get("content", "")})
        
        headers = {
            "Authorization": f"Bearer {key or 'ollama'}",
            "Content-Type": "application/json"
        }
        
        url = f"{self.base_url.rstrip('/')}/chat/completions"
        
        payload = {
            "model": model_name,
            "messages": formatted_messages,
            "temperature": temperature
        }
        
        async with httpx.AsyncClient(timeout=45.0) as client:
            resp = await client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]


class OllamaProvider(BaseLLMProvider):
    async def generate(
        self,
        system_prompt: str,
        messages: List[Dict[str, str]],
        context: Optional[str] = None,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        temperature: float = 0.7
    ) -> str:
        base_url = settings.OLLAMA_BASE_URL.rstrip('/')
        model_name = model or DEFAULT_MODELS["ollama"]
        
        sys = system_prompt
        if context:
            sys += f"\n\nContexto:\n{context}"
        
        msgs = [{"role": "system", "content": sys}] + messages
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                f"{base_url}/api/chat",
                json={
                    "model": model_name,
                    "messages": msgs,
                    "stream": False,
                    "options": {"temperature": temperature}
                }
            )
            resp.raise_for_status()
            data = resp.json()
            return data.get("message", {}).get("content", "")


class UniversalLLMAdapter:
    """
    Roteador Central Unificado de Provedores com Fallback Hermenêutico.
    """
    def __init__(self):
        self.providers: Dict[str, BaseLLMProvider] = {
            "gemini": GeminiProvider(),
            "google": GeminiProvider(),
            "claude": ClaudeProvider(),
            "anthropic": ClaudeProvider(),
            "openai": OpenAICompatibleProvider("openai"),
            "deepseek": OpenAICompatibleProvider("deepseek"),
            "perplexity": OpenAICompatibleProvider("perplexity"),
            "xai": OpenAICompatibleProvider("xai"),
            "grok": OpenAICompatibleProvider("xai"),
            "kimi": OpenAICompatibleProvider("kimi"),
            "moonshot": OpenAICompatibleProvider("moonshot"),
            "qwen": OpenAICompatibleProvider("qwen"),
            "ollama": OllamaProvider()
        }

    def get_provider(self, provider_name: str) -> BaseLLMProvider:
        key = provider_name.lower().strip()
        if key in self.providers:
            return self.providers[key]
        # Se for um endpoint compatível novo, inicializa dinamicamente
        return OpenAICompatibleProvider(key)

    async def execute_socratic_inference(
        self,
        system_prompt: str,
        messages: List[Dict[str, str]],
        context: Optional[str] = None,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        bloom_level: str = "Entender",
        camada_iave: str = "Camada 2: Análise Retórico-Estilística"
    ) -> Dict[str, Any]:
        target_provider = (provider or settings.DEFAULT_LLM_PROVIDER).lower()
        provider_instance = self.get_provider(target_provider)
        
        try:
            texto_gerado = await provider_instance.generate(
                system_prompt=system_prompt,
                messages=messages,
                context=context,
                model=model,
                api_key=api_key
            )
            return {
                "content": texto_gerado,
                "provider": target_provider,
                "model": model or DEFAULT_MODELS.get(target_provider, "default"),
                "fallback_triggered": False
            }
        except Exception as e:
            print(f"[UniversalLLMAdapter] Erro no provedor '{target_provider}': {e}. Acionando Fallback Hermenêutico.")
            fallback_text = self._generate_hermeneutic_fallback(
                messages=messages,
                context=context,
                bloom_level=bloom_level,
                camada_iave=camada_iave
            )
            return {
                "content": fallback_text,
                "provider": "hermeneutic_fallback_local",
                "model": "offline_expert_rule_v2",
                "fallback_triggered": True,
                "error_reason": str(e)
            }

    def _generate_hermeneutic_fallback(
        self,
        messages: List[Dict[str, str]],
        context: Optional[str] = None,
        bloom_level: str = "Entender",
        camada_iave: str = "Camada 2: Análise Retórico-Estilística"
    ) -> str:
        ultima_interacao = messages[-1]["content"] if messages else "o excerto"
        
        return (
            f"**[Mediação Socrática RELIA 2.0 • {camada_iave}]**\n\n"
            f"A sua reflexão sobre *'{ultima_interacao}'* constitui um ponto de partida analítico relevante.\n\n"
            f"Sob a perspetiva dos critérios IAVE e da Taxonomia de Bloom ({bloom_level}), "
            f"observe atentamente como o autor articula a escolha das figuras de estilo e a disposição rítmica no excerto. "
            f"De que modo a estrutura formal da passagem reforça a tese ou a crítica alegórica subjacente?\n\n"
            f"*Pista de Investigação:* Localize um verso ou oração específica no texto que comprove a sua interpretação antes de avançarmos."
        )

llm_adapter = UniversalLLMAdapter()
