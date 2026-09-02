from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime

# Token & Auth
class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    nome: str
    email: str
    role: str

class TokenPayload(BaseModel):
    sub: Optional[str] = None
    exp: Optional[int] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class UserCreate(BaseModel):
    nome: str
    email: EmailStr
    password: str
    idade: Optional[int] = None
    cidade: Optional[str] = None
    interesses: Optional[str] = None
    nivel_educacional: Optional[str] = None
    habito_leitura: Optional[str] = None

class UserUpdate(BaseModel):
    nome: Optional[str] = None
    idade: Optional[int] = None
    cidade: Optional[str] = None
    interesses: Optional[str] = None
    nivel_educacional: Optional[str] = None
    habito_leitura: Optional[str] = None

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    email: str
    idade: Optional[int]
    cidade: Optional[str]
    interesses: Optional[str]
    nivel_educacional: Optional[str]
    habito_leitura: Optional[str]
    role: str
    created_at: datetime

# Obras & Excertos
class ExcertoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    secao: str
    estrofes: Optional[str]
    texto: str
    analise_retorica: Optional[str]
    ordem: int

class CapituloResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    numero: int
    nome: str
    excertos: List[ExcertoResponse] = []

class ObraResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    titulo: str
    autor: str
    epoca: Optional[str]
    genero: Optional[str]
    descricao: Optional[str]
    capa_url: Optional[str]
    capitulos: List[CapituloResponse] = []

# Roteiros & Progresso
class RoteiroPasso(BaseModel):
    ordem: int
    titulo: str
    descricao: str
    nivel_bloom: str
    secao_alvo: str
    pergunta_guia: str

class RoteiroResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    obra_id: int
    titulo: str
    descricao: Optional[str]
    passos_json: List[Dict[str, Any]]

class ProgressoUpdate(BaseModel):
    obra_id: int
    passo_atual: int
    total_passos: int
    pontuacao_adicional: Optional[int] = 0

class ProgressoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    obra_id: int
    passo_atual: int
    total_passos: int
    percentual_concluido: float
    pontuacao_total: int
    ultimo_acesso: datetime

# Chat Socrático
class ChatMessageCreate(BaseModel):
    content: str
    obra_id: Optional[int] = None
    canto_ou_capitulo: Optional[int] = None
    secao: Optional[str] = None
    bloom_level: Optional[str] = "Entender"

class ChatMessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    role: str
    content: str
    bloom_level: Optional[str]
    created_at: datetime

# Checkpoint & Avaliação
class CheckpointSubmit(BaseModel):
    obra_id: int
    nivel_bloom: str
    pergunta: str
    resposta_aluno: str
    criterios_referencia: Optional[List[str]] = []
    resposta_modelo: Optional[str] = None

class CheckpointFeedbackResponse(BaseModel):
    pontuacao: float
    nivel_bloom: str
    feedback_empatico: str
    pontos_fortes: List[str]
    lacunas_argumentativas: List[str]
    leitura_sustentada: bool
    sugestao_aprofundamento: str

# Painel Delphi Peritos
class DelphiLogCreate(BaseModel):
    perito_identificador: str
    skill_avaliada: str
    prompt_ou_contexto: str
    resposta_agente: str
    nota_qualidade_likert: int
    concordancia_hermeneutica: bool
    observacoes_qualitativas: Optional[str] = None
