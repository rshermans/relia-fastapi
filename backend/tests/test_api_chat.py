"""
Testes da API de Chat Socrático Agêntico.
Cobre: criação de sessão, envio de mensagem, persistência do histórico.
"""

import pytest
from backend.app.database.models import Obra, CapituloOuCanto, Excerto


@pytest.fixture
def obra_com_excerto(client, db_engine):
    """Insere obra com excerto para testes de chat."""
    from sqlalchemy.orm import sessionmaker
    Session = sessionmaker(bind=db_engine, expire_on_commit=False)
    db = Session()
    try:
        obra = Obra(
            slug="os-lusiadas",
            titulo="Os Lusíadas",
            autor="Luís de Camões",
            epoca="Renascimento",
            genero="Épico",
        )
        db.add(obra)
        db.commit()

        canto = CapituloOuCanto(obra_id=obra.id, numero=5, nome="Canto V")
        db.add(canto)
        db.commit()

        excerto = Excerto(
            capitulo_id=canto.id,
            secao="O Gigante Adamastor",
            texto="Não acabava, quando uma figura se nos mostra no ar...",
            ordem=1,
        )
        db.add(excerto)
        db.commit()
        return obra
    finally:
        db.close()


class TestSessaoChat:
    def test_obter_ou_criar_sessao(self, client, auth_headers, obra_com_excerto):
        response = client.get(
            f"/api/chat/sessao/{obra_com_excerto.id}",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert data["titulo"].startswith("Diálogo Socrático")
        assert data["mensagens"] == []

    def test_sessao_idempotente(self, client, auth_headers, obra_com_excerto):
        """Duas chamadas devem retornar a mesma sessão."""
        r1 = client.get(f"/api/chat/sessao/{obra_com_excerto.id}", headers=auth_headers)
        r2 = client.get(f"/api/chat/sessao/{obra_com_excerto.id}", headers=auth_headers)
        assert r1.json()["session_id"] == r2.json()["session_id"]


class TestEnviarMensagem:
    def test_enviar_e_receber_resposta_agentica(self, client, auth_headers, obra_com_excerto):
        response = client.post("/api/chat/enviar", headers=auth_headers, json={
            "content": "O que significa o Adamastor como alegoria?",
            "obra_id": obra_com_excerto.id,
            "canto_ou_capitulo": 5,
            "secao": "O Gigante Adamastor",
            "bloom_level": "Analisar",
        })
        assert response.status_code == 200
        data = response.json()
        assert "user_message_id" in data
        assert data["assistant_message"]["role"] == "assistant"
        assert len(data["assistant_message"]["content"]) > 10
        assert data["assistant_message"]["bloom_level"] == "Analisar"

    def test_historico_persistido(self, client, auth_headers, obra_com_excerto):
        # Enviar mensagem
        client.post("/api/chat/enviar", headers=auth_headers, json={
            "content": "Quem é o Adamastor?",
            "obra_id": obra_com_excerto.id,
            "bloom_level": "Lembrar",
        })
        # Verificar histórico
        response = client.get(
            f"/api/chat/sessao/{obra_com_excerto.id}",
            headers=auth_headers,
        )
        mensagens = response.json()["mensagens"]
        assert len(mensagens) >= 2  # user + assistant
        roles = [m["role"] for m in mensagens]
        assert "user" in roles
        assert "assistant" in roles
