from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from backend.app.database.session import get_db
from backend.app.database.models import Usuario, Checkpoint, ProgressoLeitura
from backend.app.schemas.schemas import CheckpointSubmit, CheckpointFeedbackResponse
from backend.app.api.auth import get_current_user
from backend.app.agents.orchestrator import relia_orchestrator

router = APIRouter(prefix="/checkpoints", tags=["Checkpoints & Avaliação Metacognitiva"])

@router.post("/avaliar", response_model=CheckpointFeedbackResponse)
def submeter_e_avaliar_checkpoint(
    cp_in: CheckpointSubmit,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 1. Executar Skill 3: Avaliador Metacognitivo
    resultado = relia_orchestrator.avaliar_checkpoint_metacognitivo(
        pergunta=cp_in.pergunta,
        resposta_aluno=cp_in.resposta_aluno,
        nivel_bloom=cp_in.nivel_bloom,
        criterios_referencia=cp_in.criterios_referencia,
        resposta_modelo=cp_in.resposta_modelo
    )

    # 2. Registrar Checkpoint no Banco Local
    checkpoint_reg = Checkpoint(
        usuario_id=current_user.id,
        obra_id=cp_in.obra_id,
        nivel_bloom=cp_in.nivel_bloom,
        pergunta=cp_in.pergunta,
        resposta_aluno=cp_in.resposta_aluno,
        avaliacao_feedback=resultado["feedback_empatico"],
        pontuacao=resultado["pontuacao"],
        lacunas_argumentativas=resultado["lacunas_argumentativas"],
        leitura_sustentada=resultado["leitura_sustentada"]
    )
    db.add(checkpoint_reg)

    # 3. Atualizar pontuação no progresso
    progresso = db.query(ProgressoLeitura).filter(
        ProgressoLeitura.usuario_id == current_user.id,
        ProgressoLeitura.obra_id == cp_in.obra_id
    ).first()
    if progresso:
        progresso.pontuacao_total += int(resultado["pontuacao"] * 10)

    db.commit()

    return resultado

@router.get("/historico/{obra_id}")
def listar_historico_checkpoints(
    obra_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    checkpoints = db.query(Checkpoint).filter(
        Checkpoint.usuario_id == current_user.id,
        Checkpoint.obra_id == obra_id
    ).order_by(Checkpoint.created_at.desc()).all()
    return checkpoints
