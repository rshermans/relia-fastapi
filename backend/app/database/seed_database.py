import os
import json
from passlib.context import CryptContext
from backend.app.database.session import SessionLocal, Base, engine
from backend.app.database.models import Usuario, Obra, CapituloOuCanto, Excerto, Roteiro

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__truncate_error=True)

def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    try:
        # 1. Usuário Admin & Usuário Leitor de Teste
        admin = db.query(Usuario).filter(Usuario.email == "admin@relia.pt").first()
        if not admin:
            admin = Usuario(
                uid="admin-001",
                nome="Administrador RELIA",
                email="admin@relia.pt",
                hashed_password=pwd_context.hash("reliaAdmin2026!"),
                role="admin",
                nivel_educacional="Doutoramento / Investigação",
                habito_leitura="Avançado"
            )
            db.add(admin)

        aluno = db.query(Usuario).filter(Usuario.email == "aluno@relia.pt").first()
        if not aluno:
            aluno = Usuario(
                uid="aluno-001",
                nome="Leitor Empático",
                email="aluno@relia.pt",
                hashed_password=pwd_context.hash("leitor123"),
                role="aluno",
                idade=17,
                cidade="Braga",
                interesses="Literatura, História, Filosofia",
                nivel_educacional="12º Ano",
                habito_leitura="Semanal"
            )
            db.add(aluno)
        
        db.commit()

        # 2. Carregar Obras Canónicas
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
        obras_file = os.path.join(base_dir, "data", "seed_corpus", "obras_canonicais.json")
        
        if os.path.exists(obras_file):
            with open(obras_file, "r", encoding="utf-8") as f:
                obras_data = json.load(f)

            for item in obras_data:
                existing_obra = db.query(Obra).filter(Obra.slug == item["slug"]).first()
                if not existing_obra:
                    obra = Obra(
                        slug=item["slug"],
                        titulo=item["titulo"],
                        autor=item["autor"],
                        epoca=item.get("epoca"),
                        genero=item.get("genero"),
                        descricao=item.get("descricao")
                    )
                    db.add(obra)
                    db.commit()
                    db.refresh(obra)

                    # Adicionar Capítulos/Cantos e Excertos
                    for cap_data in item.get("capitulos_ou_cantos", []):
                        cap = CapituloOuCanto(
                            obra_id=obra.id,
                            numero=cap_data["numero"],
                            nome=cap_data["nome"]
                        )
                        db.add(cap)
                        db.commit()
                        db.refresh(cap)

                        for idx, exc_data in enumerate(cap_data.get("excertos", [])):
                            exc = Excerto(
                                capitulo_id=cap.id,
                                secao=exc_data["secao"],
                                estrofes=exc_data.get("estrofes"),
                                texto=exc_data["texto"],
                                analise_retorica=exc_data.get("analise_retorica"),
                                ordem=idx + 1
                            )
                            db.add(exc)
                    
                    # Criar Roteiro padrão guiado pela Taxonomia de Bloom
                    passos_roteiro = [
                        {
                            "ordem": 1,
                            "titulo": "Reconhecimento & Contextualização",
                            "nivel_bloom": "Lembrar",
                            "descricao": "Identificação do contexto histórico, autor e estrutura da obra.",
                            "pergunta_guia": "Quais são as coordenadas históricas e estéticas fundamentais do texto?"
                        },
                        {
                            "ordem": 2,
                            "titulo": "Compreensão Textual & Paráfrase",
                            "nivel_bloom": "Entender",
                            "descricao": "Leitura atenta dos excertos e compreensão do sentido literal e alegórico.",
                            "pergunta_guia": "Qual é a mensagem nuclear ou o conceito predicável desenvolvido pelo autor?"
                        },
                        {
                            "ordem": 3,
                            "titulo": "Análise Retórica & Estilística",
                            "nivel_bloom": "Analisar",
                            "descricao": "Identificação de figuras de estilo, estruturas sintáticas e dicotomias.",
                            "pergunta_guia": "Como as escolhas lexicais e retóricas ampliam a força persuasiva do texto?"
                        },
                        {
                            "ordem": 4,
                            "titulo": "Avaliação Crítica & Hermenêutica",
                            "nivel_bloom": "Avaliar",
                            "descricao": "Juízo de valor sustentado sobre a eficácia dos argumentos e a moral da obra.",
                            "pergunta_guia": "Até que ponto o texto atinge o seu propósito ético ou épico?"
                        },
                        {
                            "ind": 5,
                            "ordem": 5,
                            "titulo": "Transposição & Criação Empática",
                            "nivel_bloom": "Criar",
                            "descricao": "Reinterpretação do dilema textual em cenários contemporâneos ou produção reflexiva.",
                            "pergunta_guia": "Que analogia contemporânea pode ser formulada a partir do dilema da obra?"
                        }
                    ]

                    roteiro = Roteiro(
                        obra_id=obra.id,
                        titulo=f"Roteiro de Leitura Empática: {obra.titulo}",
                        descricao=f"Percurso de leitura graduado pela Taxonomia de Bloom para {obra.titulo}.",
                        passos_json=passos_roteiro
                    )
                    db.add(roteiro)
                    db.commit()

        print("Base de dados SQLite local populada com sucesso!")
    finally:
        db.close()

if __name__ == "__main__":
    seed()
