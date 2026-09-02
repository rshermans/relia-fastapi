import pytest
from backend.app.skills.extrator_discursivo import extrator_discursivo_service
from backend.app.skills.formulador_socratico import formulador_socratico_service
from backend.app.skills.avaliador_metacognitivo import avaliador_metacognitivo_service
from backend.app.agents.mcp_client import mcp_corpus_client

def test_skill_1_extrator_discursivo():
    texto_adamastor = (
        "Não acabava, quando uma figura se nos mostra no ar, robusta e válida, "
        "de disforme e grandíssima estatura; o rosto carregado, a boca negra, os dentes amarelos. "
        "Arrepiam-se as carnes e o cabelo a mi e a todos, só de ouvi-lo e vê-lo!"
    )
    resultado = extrator_discursivo_service.analisar_excerto(texto_adamastor)
    assert "estatisticas_textuais" in resultado
    assert resultado["estatisticas_textuais"]["total_palavras"] > 10
    assert len(resultado["figuras_de_estilo"]) > 0

def test_skill_2_formulador_socratico():
    resultado = formulador_socratico_service.gerar_pergunta_socratica(
        obra_titulo="Os Lusíadas",
        secao_titulo="O Gigante Adamastor",
        excerto_texto="Não acabava quando uma figura...",
        nivel_bloom="Analisar"
    )
    assert resultado["nivel_bloom"] == "Analisar"
    assert "pergunta_socratica" in resultado
    assert "Adamastor" in resultado["pergunta_socratica"]

def test_skill_3_avaliador_metacognitivo():
    pergunta = "Como o Adamastor personifica os medos lusitanos?"
    resposta_boa = (
        "O Adamastor personifica o Cabo das Tormentas e os limites do oceano. "
        "Camões utiliza a hipérbole e a antítese para mostrar que a coragem lusitana supera o terror do gigante, "
        "porque a força de vontade humana e a fé transcendem os limites da própria natureza."
    )
    resultado = avaliador_metacognitivo_service.avaliar_resposta_iave(
        pergunta=pergunta,
        resposta_aluno=resposta_boa,
        nivel_bloom="Analisar"
    )
    assert resultado["nota_iave_total_20"] >= 14.0
    assert resultado["leitura_sustentada"] is True
    assert len(resultado["pontos_fortes"]) > 0

def test_mcp_corpus_client():
    obras = mcp_corpus_client.listar_obras()
    assert len(obras) >= 2
    slugs = [o["slug"] for o in obras]
    assert "os-lusiadas" in slugs
    assert "sermao-de-santo-antonio-aos-peixes" in slugs

    excerto = mcp_corpus_client.obter_excerto("os-lusiadas", 5)
    assert excerto["total_excertos_encontrados"] > 0
