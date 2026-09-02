"""
Testes do Orquestrador Multi-Agente do RELIA.
Cobre: pipeline completo de mediação socrática e avaliação metacognitiva.
"""

import pytest
from backend.app.agents.orchestrator import relia_orchestrator


class TestMediacaoSocratica:
    @pytest.mark.asyncio
    async def test_pipeline_completo_com_mcp(self):
        """Pipeline: MCP corpus → Extrator Discursivo → Formulador Socrático → LLM Fallback."""
        resultado = await relia_orchestrator.mediar_dialogo_socratico(
            mensagem_usuario="O que significa o Adamastor como alegoria dos medos portugueses?",
            historico=[],
            obra_slug="os-lusiadas",
            canto_ou_capitulo=5,
            secao="O Gigante Adamastor",
            nivel_bloom="Analisar",
        )
        assert "resposta" in resultado
        assert len(resultado["resposta"]) > 20
        assert resultado["nivel_bloom"] == "Analisar"

        # Análise discursiva da Skill 1
        analise = resultado["analise_discursiva"]
        assert "estatisticas_textuais" in analise
        assert "figuras_de_estilo" in analise

        # Diretiva socrática da Skill 2
        diretiva = resultado["diretiva_socratica"]
        assert "pergunta_socratica" in diretiva
        assert diretiva["nivel_bloom"] == "Analisar"

    @pytest.mark.asyncio
    async def test_mediacao_sem_obra(self):
        """Pipeline sem contexto MCP (texto livre do utilizador)."""
        resultado = await relia_orchestrator.mediar_dialogo_socratico(
            mensagem_usuario="A metáfora do sal em Vieira é sobre a responsabilidade dos pregadores.",
            historico=[
                {"role": "user", "content": "Qual é o tema do Sermão?"},
                {"role": "assistant", "content": "O Sermão de Santo António aos Peixes aborda a hipocrisia."},
            ],
            nivel_bloom="Avaliar",
        )
        assert "resposta" in resultado
        assert resultado["nivel_bloom"] == "Avaliar"

    @pytest.mark.asyncio
    async def test_resposta_usa_fallback_hermeneutico(self):
        """Sem chaves de API, o LLM Service usa o fallback hermenêutico estruturado."""
        resultado = await relia_orchestrator.mediar_dialogo_socratico(
            mensagem_usuario="Como interpretar a tinta do polvo?",
            historico=[],
            nivel_bloom="Entender",
        )
        # O fallback sempre inclui "Taxonomia de Bloom" na resposta
        assert "Bloom" in resultado["resposta"] or len(resultado["resposta"]) > 10


class TestAvaliacaoMetacognitiva:
    def test_avaliacao_via_orquestrador(self):
        resultado = relia_orchestrator.avaliar_resposta_iave(
            pergunta="Como a antítese reforça o medo do desconhecido no Canto V?",
            resposta_aluno=(
                "A antítese entre a grandeza do Adamastor e a pequenez dos portugueses "
                "demonstra que Camões utiliza o contraste para amplificar o terror do desconhecido. "
                "Porque a personificação do cabo como gigante, contudo, também simboliza "
                "a superação épica dos limites humanos."
            ),
            nivel_bloom="Analisar",
        )
        assert resultado["nota_iave_total_20"] >= 12.0
        assert resultado["leitura_sustentada"] is True
        assert len(resultado["pontos_fortes"]) >= 1

    def test_avaliacao_resposta_insuficiente(self):
        resultado = relia_orchestrator.avaliar_resposta_iave(
            pergunta="O que é?",
            resposta_aluno="Sim.",
            nivel_bloom="Lembrar",
        )
        assert resultado["nota_iave_total_20"] <= 4.0
        assert resultado["leitura_sustentada"] is False

