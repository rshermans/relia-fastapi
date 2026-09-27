"""
LangGraph Orchestrator for RELIA 2.0 / PhD Skills
Implements a state graph chaining the 3 fundamental PhD skills:
1. Extrator Discursivo (Stylistic & rhetorical analysis)
2. Formulador Socrático (Bloom taxonomy & IAVE 4-layer scaffolding)
3. Avaliador Metacognitivo (Empathetic feedback & argumentation rubric)
"""

from typing import Dict, Any, List, Optional, TypedDict
from langgraph.graph import StateGraph, START, END

from backend.app.skills.extrator_discursivo import extrator_discursivo_service
from backend.app.skills.formulador_socratico import formulador_socratico_service
from backend.app.skills.avaliador_metacognitivo import avaliador_metacognitivo_service
from backend.app.agents.mcp_client import mcp_corpus_client
from backend.app.services.llm_service import llm_service


class ReliaGraphState(TypedDict):
    """Estado partilhado através dos nós do grafo LangGraph no RELIA."""
    mensagem_usuario: str
    historico: List[Dict[str, str]]
    obra_slug: Optional[str]
    canto_ou_capitulo: Optional[int]
    secao: Optional[str]
    nivel_bloom: str
    camada_iave_id: str
    provider: Optional[str]
    model: Optional[str]
    api_key: Optional[str]
    
    # Campos preenchidos pelos nós
    obra_titulo: str
    contexto_texto: str
    analise_previa: str
    analise_discursiva: Dict[str, Any]
    diretiva_socratica: Dict[str, Any]
    prompt_sistema: str
    contexto_completo: str
    resposta_conteudo: str
    metadados_llm: Dict[str, Any]
    avaliacao_metacognitiva: Optional[Dict[str, Any]]


def no_recuperar_corpus(state: ReliaGraphState) -> Dict[str, Any]:
    """Nó 1: Recuperação do excerto canónico via MCP / Base Local."""
    obra_slug = state.get("obra_slug")
    canto_ou_capitulo = state.get("canto_ou_capitulo")
    secao = state.get("secao")
    
    obra_titulo = obra_slug or "Obra Literária"
    contexto_texto = ""
    analise_previa = ""

    if obra_slug and canto_ou_capitulo:
        dados_excerto = mcp_corpus_client.obter_excerto(obra_slug, canto_ou_capitulo, secao)
        if "excertos" in dados_excerto and dados_excerto["excertos"]:
            exc = dados_excerto["excertos"][0]
            contexto_texto = exc.get("texto", "")
            analise_previa = exc.get("analise_retorica", "")
            obra_titulo = dados_excerto.get("obra", obra_slug)

    return {
        "obra_titulo": obra_titulo,
        "contexto_texto": contexto_texto,
        "analise_previa": analise_previa
    }


def no_extrator_discursivo(state: ReliaGraphState) -> Dict[str, Any]:
    """Nó 2: Skill 1 - Análise retórico-estilística (spaCy + PLN)."""
    texto = state.get("contexto_texto") or state.get("mensagem_usuario", "")
    analise_previa = state.get("analise_previa", "")
    
    analise = extrator_discursivo_service.analisar_excerto(
        texto=texto,
        analise_previa=analise_previa
    )
    return {"analise_discursiva": analise}


def no_formulador_socratico(state: ReliaGraphState) -> Dict[str, Any]:
    """Nó 3: Skill 2 - Formulação de perguntas graduadas (Taxonomia de Bloom + 4 Camadas IAVE)."""
    obra_titulo = state.get("obra_titulo", "Obra Literária")
    secao = state.get("secao") or "Excerto em análise"
    contexto_texto = state.get("contexto_texto", "")
    nivel_bloom = state.get("nivel_bloom", "Entender")
    camada_iave_id = state.get("camada_iave_id", "camada_2")

    diretiva = formulador_socratico_service.gerar_pergunta_socratica(
        obra_titulo=obra_titulo,
        secao_titulo=secao,
        excerto_texto=contexto_texto,
        nivel_bloom=nivel_bloom,
        camada_iave_id=camada_iave_id
    )

    analise_estilistica = state.get("analise_discursiva", {})
    figuras = analise_estilistica.get("figuras_de_estilo", [])
    campos = analise_estilistica.get("campos_lexicais", [])
    camada_nome = diretiva.get("camada_iave", "Camada 2: Análise Retórico-Estilística")

    prompt_sistema = (
        f"Você é o Professor Literário Automatizado do RELIA 2.0 (Orquestrado por LangGraph).\n"
        f"Orientando o estudante na: [{camada_nome}].\n\n"
        f"Princípios Pragmático-Discursivos:\n"
        f"1. Não forneça a resposta pronta;\n"
        f"2. Conduza por perguntas abertas graduadas por Bloom ({nivel_bloom});\n"
        f"3. Incentive interpretação do valor expressivo das figuras ({', '.join(figuras[:3])});\n"
        f"4. Valorize citações explícitas do excerto;\n"
        f"5. Responda em Português de Portugal culto e empático."
    )

    contexto_completo = (
        f"Obra: {obra_titulo}\n"
        f"Passagem / Excerto:\n{contexto_texto}\n\n"
        f"Figuras de Estilo Detetadas: {', '.join(figuras)}\n"
        f"Campos Lexicais: {', '.join(campos)}\n"
        f"Questão Socrática IAVE: {diretiva.get('pergunta_socratica', '')}"
    )

    return {
        "diretiva_socratica": diretiva,
        "prompt_sistema": prompt_sistema,
        "contexto_completo": contexto_completo
    }


async def no_gerador_resposta_llm(state: ReliaGraphState) -> Dict[str, Any]:
    """Nó 4: Invocação Multi-LLM assíncrona com fallback hermenêutico."""
    historico = state.get("historico", [])
    mensagem_usuario = state.get("mensagem_usuario", "")
    mensagens_completas = list(historico) + [{"role": "user", "content": mensagem_usuario}]

    diretiva = state.get("diretiva_socratica", {})
    camada_nome = diretiva.get("camada_iave", "Camada 2: Análise Retórico-Estilística")

    resultado_llm = await llm_service.gerar_resposta_socratica(
        prompt_sistema=state.get("prompt_sistema", ""),
        mensagens_historico=mensagens_completas,
        contexto_corpus=state.get("contexto_completo", ""),
        nivel_bloom=state.get("nivel_bloom", "Entender"),
        camada_iave=camada_nome,
        provider=state.get("provider"),
        model=state.get("model"),
        api_key=state.get("api_key")
    )

    return {
        "resposta_conteudo": resultado_llm.get("content", ""),
        "metadados_llm": {
            "provider": resultado_llm.get("provider", "local"),
            "model": resultado_llm.get("model", "default"),
            "fallback_triggered": resultado_llm.get("fallback_triggered", False)
        }
    }


def criar_grafo_relia():
    """Constrói e compila o StateGraph do LangGraph para mediação leitora."""
    workflow = StateGraph(ReliaGraphState)

    # Adicionar Nós
    workflow.add_node("recuperar_corpus", no_recuperar_corpus)
    workflow.add_node("extrator_discursivo", no_extrator_discursivo)
    workflow.add_node("formulador_socratico", no_formulador_socratico)
    workflow.add_node("gerador_resposta_llm", no_gerador_resposta_llm)

    # Definir Fluxo (Arestas)
    workflow.add_edge(START, "recuperar_corpus")
    workflow.add_edge("recuperar_corpus", "extrator_discursivo")
    workflow.add_edge("extrator_discursivo", "formulador_socratico")
    workflow.add_edge("formulador_socratico", "gerador_resposta_llm")
    workflow.add_edge("gerador_resposta_llm", END)

    return workflow.compile()


# Instância compilada pronta para reuso
relia_langgraph_app = criar_grafo_relia()


class ReliaLangGraphOrchestrator:
    """Interface executável para o pipeline LangGraph no RELIA."""

    def __init__(self):
        self.app = relia_langgraph_app

    async def executar_dialogo(
        self,
        mensagem_usuario: str,
        historico: Optional[List[Dict[str, str]]] = None,
        obra_slug: Optional[str] = None,
        canto_ou_capitulo: Optional[int] = None,
        secao: Optional[str] = None,
        nivel_bloom: str = "Entender",
        camada_iave_id: str = "camada_2",
        provider: Optional[str] = None,
        model: Optional[str] = None,
        api_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """Executa o grafo LangGraph de forma assíncrona."""
        estado_inicial: ReliaGraphState = {
            "mensagem_usuario": mensagem_usuario,
            "historico": historico or [],
            "obra_slug": obra_slug,
            "canto_ou_capitulo": canto_ou_capitulo,
            "secao": secao,
            "nivel_bloom": nivel_bloom,
            "camada_iave_id": camada_iave_id,
            "provider": provider,
            "model": model,
            "api_key": api_key,
            "obra_titulo": "",
            "contexto_texto": "",
            "analise_previa": "",
            "analise_discursiva": {},
            "diretiva_socratica": {},
            "prompt_sistema": "",
            "contexto_completo": "",
            "resposta_conteudo": "",
            "metadados_llm": {},
            "avaliacao_metacognitiva": None
        }

        resultado = await self.app.ainvoke(estado_inicial)
        
        return {
            "resposta": resultado.get("resposta_conteudo", ""),
            "provedor_utilizado": resultado.get("metadados_llm", {}).get("provider", "local"),
            "modelo_utilizado": resultado.get("metadados_llm", {}).get("model", "default"),
            "fallback_acionado": resultado.get("metadados_llm", {}).get("fallback_triggered", False),
            "camada_iave": resultado.get("diretiva_socratica", {}).get("camada_iave", ""),
            "camada_iave_id": camada_iave_id,
            "nivel_bloom": nivel_bloom,
            "analise_discursiva": resultado.get("analise_discursiva", {}),
            "diretiva_socratica": resultado.get("diretiva_socratica", {})
        }


relia_langgraph_orchestrator = ReliaLangGraphOrchestrator()
