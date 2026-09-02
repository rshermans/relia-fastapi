"""
Testes da API de Obras e integração com o Servidor MCP de Corpus.
Cobre: listagem, busca por slug, capítulos, busca MCP e itens de exame.
"""

import pytest
from backend.app.database.models import Obra, CapituloOuCanto, Excerto


@pytest.fixture
def seeded_obras(client, db_engine):
    """Insere obras de teste na BD via seed."""
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
            descricao="Epopeia nacional portuguesa.",
        )
        db.add(obra)
        db.commit()

        canto = CapituloOuCanto(obra_id=obra.id, numero=5, nome="Canto V")
        db.add(canto)
        db.commit()

        excerto = Excerto(
            capitulo_id=canto.id,
            secao="O Gigante Adamastor",
            estrofes="37-60",
            texto="Não acabava, quando uma figura se nos mostra no ar...",
            analise_retorica="Prosopopeia, hipérbole, antítese.",
            ordem=1,
        )
        db.add(excerto)
        db.commit()
        return obra
    finally:
        db.close()


class TestListarObras:
    def test_listar_obras_vazio(self, client):
        response = client.get("/api/obras")
        assert response.status_code == 200
        assert response.json() == []

    def test_listar_obras_com_dados(self, client, seeded_obras):
        response = client.get("/api/obras")
        assert response.status_code == 200
        obras = response.json()
        assert len(obras) >= 1
        assert obras[0]["slug"] == "os-lusiadas"


class TestObraPorSlug:
    def test_obra_encontrada(self, client, seeded_obras):
        response = client.get("/api/obras/os-lusiadas")
        assert response.status_code == 200
        data = response.json()
        assert data["titulo"] == "Os Lusíadas"
        assert data["autor"] == "Luís de Camões"
        assert len(data["capitulos"]) >= 1

    def test_obra_nao_encontrada(self, client):
        response = client.get("/api/obras/obra-inexistente")
        assert response.status_code == 404


class TestCapitulos:
    def test_listar_capitulos(self, client, seeded_obras):
        response = client.get("/api/obras/os-lusiadas/capitulos")
        assert response.status_code == 200
        caps = response.json()
        assert len(caps) >= 1
        assert caps[0]["nome"] == "Canto V"
        assert len(caps[0]["excertos"]) >= 1


class TestMCPIntegration:
    """Testes de integração com as ferramentas MCP de corpus."""

    def test_buscar_anotacoes(self, client):
        response = client.get("/api/obras/mcp/busca", params={"query": "Adamastor"})
        assert response.status_code == 200
        # O resultado depende dos dados JSON do corpus

    def test_itens_exames(self, client):
        response = client.get("/api/obras/mcp/exames")
        assert response.status_code == 200

    def test_matriz_bloom(self, client):
        response = client.get("/api/obras/mcp/bloom-matriz")
        assert response.status_code == 200
