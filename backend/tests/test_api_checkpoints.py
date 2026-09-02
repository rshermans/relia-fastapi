"""
Testes da API de Checkpoints e Avaliação Metacognitiva (Skill 3).
Cobre: submissão de checkpoint, avaliação, histórico.
"""

import pytest
from backend.app.database.models import Obra


@pytest.fixture
def obra_teste(client, db_engine):
    """Insere obra mínima para testes de checkpoint."""
    from sqlalchemy.orm import sessionmaker
    Session = sessionmaker(bind=db_engine)
    db = Session()
    try:
        obra = Obra(
            slug="sermao-peixes",
            titulo="Sermão de Santo António aos Peixes",
            autor="Padre António Vieira",
            epoca="Barroco",
            genero="Oratória",
        )
        db.add(obra)
        db.commit()
        db.refresh(obra)
        return obra
    finally:
        db.close()


class TestSubmissaoCheckpoint:
    def test_avaliar_resposta_boa(self, client, auth_headers, obra_teste):
        response = client.post("/api/checkpoints/avaliar", headers=auth_headers, json={
            "obra_id": obra_teste.id,
            "nivel_bloom": "Analisar",
            "pergunta": "Como o polvo simboliza a hipocrisia no Sermão?",
            "resposta_aluno": (
                "O polvo, porque utiliza a tinta para se camuflar, "
                "simboliza a hipocrisia humana segundo Vieira. A metáfora "
                "demonstra que os hipócritas se escondem atrás de disfarces, "
                "embora a sua verdadeira natureza seja visível para quem os observa."
            ),
        })
        assert response.status_code == 200
        data = response.json()
        assert data["pontuacao"] >= 6.0
        assert data["nivel_bloom"] == "Analisar"
        assert "feedback_empatico" in data
        assert isinstance(data["pontos_fortes"], list)
        assert isinstance(data["lacunas_argumentativas"], list)
        assert isinstance(data["leitura_sustentada"], bool)

    def test_avaliar_resposta_curta(self, client, auth_headers, obra_teste):
        response = client.post("/api/checkpoints/avaliar", headers=auth_headers, json={
            "obra_id": obra_teste.id,
            "nivel_bloom": "Entender",
            "pergunta": "O que é o polvo?",
            "resposta_aluno": "Um peixe.",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["pontuacao"] <= 4.0
        assert data["leitura_sustentada"] is False


class TestHistoricoCheckpoints:
    def test_historico_vazio(self, client, auth_headers, obra_teste):
        response = client.get(
            f"/api/checkpoints/historico/{obra_teste.id}",
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json() == []

    def test_historico_apos_submissao(self, client, auth_headers, obra_teste):
        # Submeter checkpoint
        client.post("/api/checkpoints/avaliar", headers=auth_headers, json={
            "obra_id": obra_teste.id,
            "nivel_bloom": "Lembrar",
            "pergunta": "Quem é Vieira?",
            "resposta_aluno": "Padre António Vieira foi um orador barroco português.",
        })
        # Verificar histórico
        response = client.get(
            f"/api/checkpoints/historico/{obra_teste.id}",
            headers=auth_headers,
        )
        assert response.status_code == 200
        historico = response.json()
        assert len(historico) >= 1
