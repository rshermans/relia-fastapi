from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

from backend.app.database.session import get_db
from backend.app.database.models import Usuario, Obra, ChatSession, ChatMessage, Checkpoint
from backend.app.schemas.schemas import ChatMessageCreate, ChatMessageResponse
from backend.app.api.auth import get_current_user
from backend.app.agents.orchestrator import relia_orchestrator
from backend.app.api.llm_config import SESSION_API_KEYS, SESSION_ACTIVE_MODELS

router = APIRouter(prefix="/chat", tags=["Chat Socrático Agêntico & Mediação IAVE"])

class ChatMessageExtendedCreate(BaseModel):
    obra_id: Optional[int] = None
    canto_ou_capitulo: Optional[int] = None
    secao: Optional[str] = None
    content: str
    bloom_level: Optional[str] = "Entender"
    camada_iave_id: Optional[str] = "camada_2"
    provider: Optional[str] = None
    model: Optional[str] = None
    api_key: Optional[str] = None

class AvaliarIAVERequest(BaseModel):
    pergunta: str
    resposta_aluno: str
    excerto_referencia: Optional[str] = None
    camada_iave_id: str = "camada_2"
    nivel_bloom: str = "Entender"
    obra_id: Optional[int] = None

@router.get("/sessao/{obra_id}")
def obter_ou_criar_sessao(obra_id: int, current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    sessao = db.query(ChatSession).filter(
        ChatSession.usuario_id == current_user.id,
        ChatSession.obra_id == obra_id
    ).first()
    
    if not sessao:
        obra = db.query(Obra).filter(Obra.id == obra_id).first()
        titulo = f"Diálogo Socrático: {obra.titulo}" if obra else "Diálogo Socrático"
        sessao = ChatSession(usuario_id=current_user.id, obra_id=obra_id, titulo=titulo)
        db.add(sessao)
        db.commit()
        db.refresh(sessao)

    mensagens = db.query(ChatMessage).filter(ChatMessage.session_id == sessao.id).order_by(ChatMessage.created_at.asc()).all()
    return {
        "session_id": sessao.id,
        "titulo": sessao.titulo,
        "mensagens": [
            {
                "id": m.id,
                "role": m.role,
                "content": m.content,
                "bloom_level": m.bloom_level,
                "metadata": m.metadata_json,
                "created_at": m.created_at
            }
            for m in mensagens
        ]
    }

@router.post("/enviar")
async def enviar_mensagem(
    msg_in: ChatMessageExtendedCreate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Obter ou criar sessão
    sessao = db.query(ChatSession).filter(
        ChatSession.usuario_id == current_user.id,
        ChatSession.obra_id == msg_in.obra_id
    ).first()

    if not sessao:
        sessao = ChatSession(usuario_id=current_user.id, obra_id=msg_in.obra_id)
        db.add(sessao)
        db.commit()
        db.refresh(sessao)

    # 1. Salvar mensagem do usuário
    user_msg = ChatMessage(
        session_id=sessao.id,
        role="user",
        content=msg_in.content,
        bloom_level=msg_in.bloom_level,
        metadata_json={"camada_iave_id": msg_in.camada_iave_id}
    )
    db.add(user_msg)
    db.commit()

    # 2. Carregar histórico recente
    mensagens_passadas = db.query(ChatMessage).filter(ChatMessage.session_id == sessao.id).order_by(ChatMessage.created_at.asc()).limit(10).all()
    historico = [{"role": m.role, "content": m.content} for m in mensagens_passadas]

    # Obter slug da obra
    obra_slug = None
    if msg_in.obra_id:
        obra = db.query(Obra).filter(Obra.id == msg_in.obra_id).first()
        if obra:
            obra_slug = obra.slug

    # Resolver provedor e chave se informados ou em sessão
    target_prov = msg_in.provider
    custom_key = msg_in.api_key or (SESSION_API_KEYS.get(target_prov) if target_prov else None)
    target_model = msg_in.model or (SESSION_ACTIVE_MODELS.get(target_prov) if target_prov else None)

    # 3. Invocar Orquestrador Agêntico
    resultado_agente = await relia_orchestrator.mediar_dialogo_socratico(
        mensagem_usuario=msg_in.content,
        historico=historico,
        obra_slug=obra_slug,
        canto_ou_capitulo=msg_in.canto_ou_capitulo,
        secao=msg_in.secao,
        nivel_bloom=msg_in.bloom_level or "Entender",
        camada_iave_id=msg_in.camada_iave_id or "camada_2",
        provider=target_prov,
        model=target_model,
        api_key=custom_key
    )

    # 4. Salvar resposta do assistente
    bot_msg = ChatMessage(
        session_id=sessao.id,
        role="assistant",
        content=resultado_agente["resposta"],
        bloom_level=msg_in.bloom_level,
        metadata_json={
            "provedor": resultado_agente.get("provedor_utilizado"),
            "modelo": resultado_agente.get("modelo_utilizado"),
            "fallback_acionado": resultado_agente.get("fallback_acionado"),
            "camada_iave": resultado_agente.get("camada_iave"),
            "analise_discursiva": resultado_agente.get("analise_discursiva"),
            "diretiva_socratica": resultado_agente.get("diretiva_socratica")
        }
    )
    db.add(bot_msg)
    db.commit()
    db.refresh(bot_msg)

    return {
        "user_message_id": user_msg.id,
        "assistant_message": {
            "id": bot_msg.id,
            "role": "assistant",
            "content": bot_msg.content,
            "bloom_level": bot_msg.bloom_level,
            "metadata": bot_msg.metadata_json,
            "created_at": bot_msg.created_at
        }
    }

@router.post("/avaliar-iave")
def avaliar_resposta_com_grelha_iave(
    payload: AvaliarIAVERequest,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Avalia a resposta do aluno com base na grelha oficial IAVE (Parâmetros C, F, E)
    e persiste o registo no banco para análise empírica do doutoramento.
    """
    resultado_avaliacao = relia_orchestrator.avaliar_resposta_iave(
        pergunta=payload.pergunta,
        resposta_aluno=payload.resposta_aluno,
        excerto_referencia=payload.excerto_referencia,
        camada_iave_id=payload.camada_iave_id,
        nivel_bloom=payload.nivel_bloom
    )

    # Salvar Checkpoint na base de dados
    if payload.obra_id:
        cp = Checkpoint(
            usuario_id=current_user.id,
            obra_id=payload.obra_id,
            nivel_bloom=payload.nivel_bloom,
            pergunta=payload.pergunta,
            resposta_aluno=payload.resposta_aluno,
            avaliacao_feedback=resultado_avaliacao["feedback_empatico"],
            pontuacao=resultado_avaliacao["nota_iave_total_20"] / 2.0, # Normalizado para base 10
            lacunas_argumentativas=resultado_avaliacao["lacunas_argumentativas"],
            leitura_sustentada=resultado_avaliacao["leitura_sustentada"]
        )
        db.add(cp)
        db.commit()

    return resultado_avaliacao
