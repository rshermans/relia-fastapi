"""
Testes da API de Autenticação e Gestão de Utilizadores.
Cobre: registo, login, /me, perfil, e erros de autenticação.
"""

import pytest


class TestRegisto:
    def test_registo_novo_utilizador(self, client):
        response = client.post("/api/auth/register", json={
            "nome": "Maria Silva",
            "email": "maria@teste.pt",
            "password": "senhaForte456",
            "idade": 16,
            "cidade": "Lisboa",
            "nivel_educacional": "11º Ano",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["nome"] == "Maria Silva"
        assert data["email"] == "maria@teste.pt"
        assert data["role"] == "aluno"
        assert "id" in data

    def test_registo_email_duplicado(self, client, registered_user):
        response = client.post("/api/auth/register", json={
            "nome": "Outro User",
            "email": registered_user["email"],
            "password": "outraSenha",
        })
        assert response.status_code == 400
        assert "registado" in response.json()["detail"].lower()

    def test_registo_sem_campos_obrigatorios(self, client):
        response = client.post("/api/auth/register", json={
            "nome": "Incompleto",
        })
        assert response.status_code == 422


class TestLogin:
    def test_login_valido(self, client, registered_user):
        response = client.post("/api/auth/login", json={
            "email": registered_user["email"],
            "password": "senhaSegura123",
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["email"] == registered_user["email"]

    def test_login_senha_incorrecta(self, client, registered_user):
        response = client.post("/api/auth/login", json={
            "email": registered_user["email"],
            "password": "senhaErrada",
        })
        assert response.status_code == 401

    def test_login_email_inexistente(self, client):
        response = client.post("/api/auth/login", json={
            "email": "naoexiste@relia.pt",
            "password": "qualquer",
        })
        assert response.status_code == 401


class TestMe:
    def test_me_com_token_valido(self, client, auth_headers, registered_user):
        response = client.get("/api/auth/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == registered_user["email"]

    def test_me_sem_token(self, client):
        response = client.get("/api/auth/me")
        assert response.status_code == 401

    def test_me_com_token_invalido(self, client):
        response = client.get("/api/auth/me", headers={
            "Authorization": "Bearer token-invalido-xyz"
        })
        assert response.status_code == 401


class TestPerfil:
    def test_actualizar_perfil(self, client, auth_headers):
        response = client.put("/api/auth/profile", headers=auth_headers, json={
            "cidade": "Porto",
            "habito_leitura": "Diário",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["cidade"] == "Porto"
        assert data["habito_leitura"] == "Diário"
