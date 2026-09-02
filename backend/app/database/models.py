from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, Boolean, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from backend.app.database.session import Base

def utc_now():
    return datetime.now(timezone.utc)

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    uid = Column(String(64), unique=True, index=True)
    nome = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    idade = Column(Integer, nullable=True)
    cidade = Column(String(100), nullable=True)
    interesses = Column(Text, nullable=True)
    nivel_educacional = Column(String(100), nullable=True) # ex: 10º ano, 12º ano, Universitário
    habito_leitura = Column(String(100), nullable=True)
    perfil_leitor_json = Column(JSON, nullable=True)
    role = Column(String(50), default="aluno") # aluno | professor | perito | admin
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utc_now)

    progressos = relationship("ProgressoLeitura", back_populates="usuario", cascade="all, delete-orphan")
    chat_sessions = relationship("ChatSession", back_populates="usuario", cascade="all, delete-orphan")
    checkpoints = relationship("Checkpoint", back_populates="usuario", cascade="all, delete-orphan")


class Obra(Base):
    __tablename__ = "obras"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String(100), unique=True, index=True, nullable=False)
    titulo = Column(String(255), nullable=False)
    autor = Column(String(255), nullable=False)
    epoca = Column(String(100), nullable=True)
    genero = Column(String(100), nullable=True)
    descricao = Column(Text, nullable=True)
    capa_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=utc_now)

    capitulos = relationship("CapituloOuCanto", back_populates="obra", cascade="all, delete-orphan")
    roteiros = relationship("Roteiro", back_populates="obra", cascade="all, delete-orphan")


class CapituloOuCanto(Base):
    __tablename__ = "capitulos_ou_cantos"

    id = Column(Integer, primary_key=True, index=True)
    obra_id = Column(Integer, ForeignKey("obras.id"), nullable=False)
    numero = Column(Integer, nullable=False)
    nome = Column(String(255), nullable=False) # ex: 'Canto I', 'Capítulo IV'

    obra = relationship("Obra", back_populates="capitulos")
    excertos = relationship("Excerto", back_populates="capitulo", cascade="all, delete-orphan")


class Excerto(Base):
    __tablename__ = "excertos"

    id = Column(Integer, primary_key=True, index=True)
    capitulo_id = Column(Integer, ForeignKey("capitulos_ou_cantos.id"), nullable=False)
    secao = Column(String(255), nullable=False) # ex: 'O Gigante Adamastor'
    estrofes = Column(String(100), nullable=True) # ex: '37-40'
    texto = Column(Text, nullable=False)
    analise_retorica = Column(Text, nullable=True)
    ordem = Column(Integer, default=0)

    capitulo = relationship("CapituloOuCanto", back_populates="excertos")


class Roteiro(Base):
    __tablename__ = "roteiros"

    id = Column(Integer, primary_key=True, index=True)
    obra_id = Column(Integer, ForeignKey("obras.id"), nullable=False)
    titulo = Column(String(255), nullable=False)
    descricao = Column(Text, nullable=True)
    passos_json = Column(JSON, nullable=False) # Lista de passos graduados de leitura com Bloom
    created_at = Column(DateTime, default=utc_now)

    obra = relationship("Obra", back_populates="roteiros")
    progressos = relationship("ProgressoLeitura", back_populates="roteiro")


class ProgressoLeitura(Base):
    __tablename__ = "progresso_leitura"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    obra_id = Column(Integer, ForeignKey("obras.id"), nullable=False)
    roteiro_id = Column(Integer, ForeignKey("roteiros.id"), nullable=True)
    passo_atual = Column(Integer, default=1)
    total_passos = Column(Integer, default=5)
    percentual_concluido = Column(Float, default=0.0)
    pontuacao_total = Column(Integer, default=0)
    ultimo_acesso = Column(DateTime, default=utc_now)

    usuario = relationship("Usuario", back_populates="progressos")
    roteiro = relationship("Roteiro", back_populates="progressos")


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    obra_id = Column(Integer, ForeignKey("obras.id"), nullable=True)
    titulo = Column(String(255), default="Sessão de Leitura Socrática")
    created_at = Column(DateTime, default=utc_now)

    usuario = relationship("Usuario", back_populates="chat_sessions")
    mensagens = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=False)
    role = Column(String(20), nullable=False) # user | assistant | system
    content = Column(Text, nullable=False)
    bloom_level = Column(String(50), nullable=True) # Lembrar, Entender, etc.
    metadata_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=utc_now)

    session = relationship("ChatSession", back_populates="mensagens")


class Checkpoint(Base):
    __tablename__ = "checkpoints"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    obra_id = Column(Integer, ForeignKey("obras.id"), nullable=False)
    nivel_bloom = Column(String(50), nullable=False)
    pergunta = Column(Text, nullable=False)
    resposta_aluno = Column(Text, nullable=False)
    avaliacao_feedback = Column(Text, nullable=True)
    pontuacao = Column(Float, default=0.0)
    lacunas_argumentativas = Column(JSON, nullable=True)
    leitura_sustentada = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utc_now)

    usuario = relationship("Usuario", back_populates="checkpoints")


class LogDelphiPerito(Base):
    __tablename__ = "logs_delphi_peritos"

    id = Column(Integer, primary_key=True, index=True)
    perito_identificador = Column(String(100), nullable=False)
    skill_avaliada = Column(String(100), nullable=False) # Extrator, Formulador Socrático, Avaliador Metacognitivo
    prompt_ou_contexto = Column(Text, nullable=False)
    resposta_agente = Column(Text, nullable=False)
    nota_qualidade_likert = Column(Integer, nullable=True) # 1 a 5
    concordancia_hermeneutica = Column(Boolean, default=True)
    observacoes_qualitativas = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now)
