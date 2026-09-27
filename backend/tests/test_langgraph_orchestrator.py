"""
Testes unitários para o Orquestrador LangGraph do RELIA 2.0 / PhD Skills.
"""

import pytest
from backend.app.agents.langgraph_orchestrator import (
    relia_langgraph_orchestrator,
    criar_grafo_relia,
    ReliaGraphState
)


@pytest.mark.asyncio
async def test_langgraph_grafo_compila():
    """Valida se o StateGraph é compilado com todos os nós e arestas corretas."""
    app = criar_grafo_relia()
    assert app is not None
    # Verifica a existência dos nós no grafo
    nodes = app.get_graph().nodes
    assert "recuperar_corpus" in nodes
    assert "extrator_discursivo" in nodes
    assert "formulador_socratico" in nodes
    assert "gerador_resposta_llm" in nodes


@pytest.mark.asyncio
async def test_langgraph_execucao_pipeline():
    """Valida a execução de ponta a ponta do fluxo no LangGraph."""
    resultado = await relia_langgraph_orchestrator.executar_dialogo(
        mensagem_usuario="Como a anástrofe enfatiza a coragem dos navegadores?",
        obra_slug="lusiadas",
        canto_ou_capitulo=1,
        secao="Proposição",
        nivel_bloom="Analisar",
        camada_iave_id="camada_2"
    )

    assert "resposta" in resultado
    assert len(resultado["resposta"]) > 0
    assert "analise_discursiva" in resultado
    assert "diretiva_socratica" in resultado
    assert resultado["nivel_bloom"] == "Analisar"
    assert resultado["camada_iave_id"] == "camada_2"
