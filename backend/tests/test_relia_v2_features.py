import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.services.llm_adapter import llm_adapter
from backend.app.services.text_sanitizer import text_sanitizer
from backend.app.services.hermeneutic_segmenter import hermeneutic_segmenter
from backend.app.services.rag_service import rag_service
from backend.app.services.scientific_export_service import scientific_export_service
from backend.app.skills.formulador_socratico import formulador_socratico_service
from backend.app.skills.avaliador_metacognitivo import avaliador_metacognitivo_service

client = TestClient(app)

def test_health_check_v2():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert data["multi_llm_status"] == "active"
    assert data["iave_layers"] == 4

def test_text_sanitizer_gutenberg_and_stats():
    raw = """*** START OF THIS PROJECT GUTENBERG EBOOK OS LUSIADAS ***
    As armas e os barões assinalados,
    Que da ocidental praia lusitana...
    *** END OF THIS PROJECT GUTENBERG EBOOK ***"""
    cleaned, stats = text_sanitizer.normalize_literary_text(raw, is_verse=True)
    assert "*** START" not in cleaned
    assert "*** END" not in cleaned
    assert "barões assinalados" in cleaned
    assert stats["total_palavras"] > 5

def test_hermeneutic_segmenter_epic_and_hashes():
    verse_text = """CANTO PRIMEIRO

As armas e os barões assinalados,
Que da ocidental praia lusitana,
Por mares nunca de antes navegados,
Passaram ainda além da Taprobana.

E também as memórias gloriosas
Daqueles Reis, que foram dilatando
A Fé, o Império, e as terras viciosas
De África e de Ásia andaram devastando."""
    chunks = hermeneutic_segmenter.segment_epic_poetry(verse_text, "Os Lusíadas", max_strophes_per_chunk=2)
    assert len(chunks) >= 1
    first_chunk = chunks[0]
    assert "hash_sha256" in first_chunk
    assert len(first_chunk["hash_sha256"]) == 64
    assert "metricas_pln" in first_chunk
    assert first_chunk["genero"] == "Poesia Épica"

def test_transparent_rag_service():
    corpus = [
        {
            "texto": "Não acabava, quando uma figura se nos mostra no ar, de disforme e grandíssima estatura (Adamastor).",
            "camada_iave_recomendada": "Camada 2: Análise Retórico-Estilística",
            "metricas_pln": {"recursos_estilisticos_provaveis": ["Comparação", "Antítese"]}
        },
        {
            "texto": "Vos estis sal terrae: vós sois o sal da terra e os peixes ouvem mas não falam.",
            "camada_iave_recomendada": "Camada 3: Hermenêutica e Crítica Social",
            "metricas_pln": {"recursos_estilisticos_provaveis": ["Metáfora"]}
        }
    ]
    results = rag_service.search_excerpts("Adamastor monstro e tempestade", corpus, top_k=1)
    assert len(results) == 1
    assert "Adamastor" in results[0]["excerto"]["texto"]
    assert results[0]["score_similaridade"] > 0

@pytest.mark.asyncio
async def test_llm_adapter_hermeneutic_fallback():
    res = await llm_adapter.execute_socratic_inference(
        system_prompt="Você é o professor de literatura.",
        messages=[{"role": "user", "content": "O que simboliza o Adamastor?"}],
        provider="provedor_inexistente_para_testar_fallback",
        camada_iave="Camada 2: Análise Retórico-Estilística"
    )
    assert res["fallback_triggered"] is True
    assert "Mediação Socrática RELIA 2.0" in res["content"]

def test_avaliador_metacognitivo_iave_rubric():
    res = avaliador_metacognitivo_service.avaliar_resposta_iave(
        pergunta="Explicite a dimensão simbólica do Adamastor.",
        resposta_aluno='O Gigante Adamastor simboliza os perigos e o medo do mar desconhecido porque representa "a boca negra" dos elementos naturais contrapostos à coragem dos nautas.',
        camada_iave_id="camada_2"
    )
    assert res["nota_iave_total_20"] >= 10.0
    assert "parametro_c_conteudo" in res["parametros_iave"]
    assert "parametro_f_estruturacao" in res["parametros_iave"]
    assert "parametro_e_expressao" in res["parametros_iave"]
    assert res["leitura_sustentada"] is True

def test_scientific_export_service():
    dados = [
        {
            "id": 1,
            "usuario_id": 10,
            "obra_slug": "os-lusiadas",
            "camada_iave": "camada_2",
            "nivel_bloom": "Entender",
            "nota_iave_total_20": 15.0,
            "parametros_iave": {
                "parametro_c_conteudo": {"nota_percentual": 80},
                "parametro_f_estruturacao": {"nota_percentual": 75},
                "parametro_e_expressao": {"nota_percentual": 70}
            },
            "leitura_sustentada": True,
            "total_palavras": 40,
            "tempo_resposta_segundos": 60
        }
    ]
    spss_csv = scientific_export_service.export_spss_csv(dados)
    assert "id_check;id_aluno;obra_slug" in spss_csv
    assert "15.0" in spss_csv

    r_script = scientific_export_service.export_r_script(dados)
    assert "dados_relia <- fromJSON" in r_script
    assert "summary(dados_relia$nota_iave_total_20)" in r_script

def test_api_llm_providers():
    resp = client.get("/api/llm/providers")
    assert resp.status_code == 200
    providers = resp.json()
    ids = [p["id"] for p in providers]
    assert "gemini" in ids
    assert "claude" in ids
    assert "deepseek" in ids
    assert "openai" in ids
    assert "ollama" in ids

def test_api_cientifico_endpoints():
    resp_resumo = client.get("/api/cientifico/resumo-corpus")
    assert resp_resumo.status_code == 200
    assert "total_obras" in resp_resumo.json()

    resp_excertos = client.get("/api/cientifico/excertos-inspecao")
    assert resp_excertos.status_code == 200
    assert isinstance(resp_excertos.json(), list)
