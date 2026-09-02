from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from backend.app.database.session import get_db
from backend.app.database.models import Usuario, Obra, Roteiro, ProgressoLeitura
from backend.app.schemas.schemas import RoteiroResponse, ProgressoResponse, ProgressoUpdate
from backend.app.api.auth import get_current_user

router = APIRouter(prefix="/leitor", tags=["Área do Leitor & Roteiro"])

@router.get("/roteiro/{obra_id}", response_model=RoteiroResponse)
def obter_roteiro(obra_id: int, db: Session = Depends(get_db)):
    roteiro = db.query(Roteiro).filter(Roteiro.obra_id == obra_id).first()
    if not roteiro:
        raise HTTPException(status_code=404, detail="Roteiro de leitura não encontrado para esta obra.")
    return roteiro

@router.get("/progresso/{obra_id}", response_model=ProgressoResponse)
def obter_progresso(obra_id: int, current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    progresso = db.query(ProgressoLeitura).filter(
        ProgressoLeitura.usuario_id == current_user.id,
        ProgressoLeitura.obra_id == obra_id
    ).first()
    
    if not progresso:
        # Inicializa o progresso se não existir
        roteiro = db.query(Roteiro).filter(Roteiro.obra_id == obra_id).first()
        total = len(roteiro.passos_json) if roteiro else 5
        progresso = ProgressoLeitura(
            usuario_id=current_user.id,
            obra_id=obra_id,
            roteiro_id=roteiro.id if roteiro else None,
            passo_atual=1,
            total_passos=total,
            percentual_concluido=0.0,
            pontuacao_total=0
        )
        db.add(progresso)
        db.commit()
        db.refresh(progresso)

    return progresso

@router.post("/progresso/avancar", response_model=ProgressoResponse)
def avancar_progresso(update_data: ProgressoUpdate, current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    progresso = db.query(ProgressoLeitura).filter(
        ProgressoLeitura.usuario_id == current_user.id,
        ProgressoLeitura.obra_id == update_data.obra_id
    ).first()

    if not progresso:
        progresso = ProgressoLeitura(
            usuario_id=current_user.id,
            obra_id=update_data.obra_id,
            passo_atual=update_data.passo_atual,
            total_passos=update_data.total_passos
        )
        db.add(progresso)

    progresso.passo_atual = update_data.passo_atual
    progresso.total_passos = update_data.total_passos
    progresso.percentual_concluido = round((progresso.passo_atual / progresso.total_passos) * 100, 1)
    if update_data.pontuacao_adicional:
        progresso.pontuacao_total += update_data.pontuacao_adicional
    progresso.ultimo_acesso = datetime.utcnow()

    db.commit()
    db.refresh(progresso)
    return progresso
