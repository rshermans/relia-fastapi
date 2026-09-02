from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from backend.app.database.session import get_db
from backend.app.database.models import Usuario, Obra, Checkpoint, LogDelphiPerito
from backend.app.schemas.schemas import DelphiLogCreate
from backend.app.api.auth import get_current_user

router = APIRouter(prefix="/admin", tags=["Administração & Painel Delphi"])

def verify_admin(current_user: Usuario = Depends(get_current_user)):
    if current_user.role not in ["admin", "perito"]:
        raise HTTPException(status_code=403, detail="Acesso restrito a administradores e peritos do painel Delphi.")
    return current_user

@router.get("/stats")
def obter_estatisticas_gerais(admin_user: Usuario = Depends(verify_admin), db: Session = Depends(get_db)):
    total_usuarios = db.query(Usuario).count()
    total_obras = db.query(Obra).count()
    total_checkpoints = db.query(Checkpoint).count()
    total_logs_delphi = db.query(LogDelphiPerito).count()
    
    # Média de concordância Delphi
    logs_delphi = db.query(LogDelphiPerito).all()
    concordancias = [1 if l.concordancia_hermeneutica else 0 for l in logs_delphi]
    taxa_concordancia = (sum(concordancias) / len(concordancias) * 100) if concordancias else 100.0

    return {
        "total_usuarios": total_usuarios,
        "total_obras": total_obras,
        "total_avaliacoes_checkpoints": total_checkpoints,
        "total_avaliacoes_delphi": total_logs_delphi,
        "taxa_concordancia_inter_avaliadores_pct": round(taxa_concordancia, 1)
    }

@router.post("/delphi/log")
def registrar_avaliacao_delphi(
    log_in: DelphiLogCreate,
    current_user: Usuario = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    novo_log = LogDelphiPerito(
        perito_identificador=log_in.perito_identificador or current_user.email,
        skill_avaliada=log_in.skill_avaliada,
        prompt_ou_contexto=log_in.prompt_ou_contexto,
        resposta_agente=log_in.resposta_agente,
        nota_qualidade_likert=log_in.nota_qualidade_likert,
        concordancia_hermeneutica=log_in.concordancia_hermeneutica,
        observacoes_qualitativas=log_in.observacoes_qualitativas
    )
    db.add(novo_log)
    db.commit()
    db.refresh(novo_log)
    return {"message": "Avaliação do Painel Delphi registrada com sucesso!", "id": novo_log.id}

@router.get("/delphi/logs")
def listar_logs_delphi(admin_user: Usuario = Depends(verify_admin), db: Session = Depends(get_db)):
    logs = db.query(LogDelphiPerito).order_by(LogDelphiPerito.created_at.desc()).all()
    return logs
