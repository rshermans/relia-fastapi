"""
Testes da Sementeira (Seed) da Base de Dados.
Cobre: criação de utilizadores padrão, obras canónicas, roteiros de Bloom.
"""

import pytest
from sqlalchemy.orm import sessionmaker
from backend.app.database.models import Usuario, Obra, CapituloOuCanto, Excerto, Roteiro


def _get_session(db_engine):
    """Helper para criar sessão de teste."""
    Session = sessionmaker(bind=db_engine)
    return Session()


class TestSeedUtilizadores:
    def test_admin_criado(self, seeded_db, db_engine):
        db = _get_session(db_engine)
        admin = db.query(Usuario).filter(Usuario.email == "admin@relia.pt").first()
        assert admin is not None
        assert admin.role == "admin"
        db.close()

    def test_aluno_criado(self, seeded_db, db_engine):
        db = _get_session(db_engine)
        aluno = db.query(Usuario).filter(Usuario.email == "aluno@relia.pt").first()
        assert aluno is not None
        assert aluno.role == "aluno"
        assert aluno.cidade == "Braga"
        db.close()


class TestSeedObras:
    def test_lusiadas_carregados(self, seeded_db, db_engine):
        db = _get_session(db_engine)
        obra = db.query(Obra).filter(Obra.slug == "os-lusiadas").first()
        assert obra is not None
        assert "Camões" in obra.autor
        assert len(obra.capitulos) >= 1
        db.close()

    def test_sermao_carregado(self, seeded_db, db_engine):
        db = _get_session(db_engine)
        obra = db.query(Obra).filter(Obra.slug == "sermao-de-santo-antonio-aos-peixes").first()
        assert obra is not None
        assert "Vieira" in obra.autor
        db.close()

    def test_excertos_presentes(self, seeded_db, db_engine):
        db = _get_session(db_engine)
        total_excertos = db.query(Excerto).count()
        assert total_excertos >= 2, f"Esperados pelo menos 2 excertos, encontrados {total_excertos}"
        db.close()


class TestSeedRoteiros:
    def test_roteiro_bloom_criado(self, seeded_db, db_engine):
        db = _get_session(db_engine)
        roteiros = db.query(Roteiro).all()
        assert len(roteiros) >= 1
        roteiro = roteiros[0]
        assert isinstance(roteiro.passos_json, list)
        assert len(roteiro.passos_json) == 5
        niveis = [p.get("nivel_bloom") for p in roteiro.passos_json]
        assert "Lembrar" in niveis
        assert "Criar" in niveis
        db.close()
