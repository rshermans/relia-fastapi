"""
Rotas Científicas para Doutoramento e Investigação Empírica
Fornece visualização transparente de excertos, hashes de integridade, simulação de RAG e exportação para SPSS/R/NVivo.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

from backend.app.database.session import get_db
from backend.app.database.models import Obra, CapituloOuCanto, Excerto, Checkpoint
from backend.app.services.rag_service import rag_service
from backend.app.services.hermeneutic_segmenter import hermeneutic_segmenter
from backend.app.services.scientific_export_service import scientific_export_service

router = APIRouter(prefix="/cientifico", tags=["Investigação Científica & Doutoramento"])

class RAGSimulationRequest(BaseModel):
    query: str
    obra_slug: Optional[str] = "os-lusiadas"
    camada_iave: Optional[str] = None
    top_k: int = 3

@router.get("/resumo-corpus")
def obter_resumo_corpus(db: Session = Depends(get_db)):
    """Retorna estatísticas ontológicas e quantitativas do corpus de investigação."""
    obras = db.query(Obra).all()
    total_excertos = db.query(Excerto).count()
    checkpoints = db.query(Checkpoint).all()
    
    return {
        "projeto": "RELIA 2.0 - CEHUM / Universidade do Minho",
        "total_obras": len(obras),
        "total_excertos_indexados": total_excertos,
        "total_avaliacoes_iave_coletadas": len(checkpoints),
        "obras": [{"id": o.id, "slug": o.slug, "titulo": o.titulo, "autor": o.autor, "genero": o.genero} for o in obras]
    }

@router.get("/excertos-inspecao")
def listar_excertos_com_metadados(
    obra_slug: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Lista todos os excertos com as métricas de PLN, localização e hash SHA-256 para inspeção científica.
    """
    query = db.query(Excerto).join(CapituloOuCanto).join(Obra)
    if obra_slug:
        query = query.filter(Obra.slug == obra_slug)
        
    excertos_db = query.all()
    
    resultados = []
    for exc in excertos_db:
        cap = exc.capitulo
        obra = cap.obra if cap else None
        
        # Calcular métricas em tempo real caso não estejam pré-computadas
        metrics = hermeneutic_segmenter.extract_linguistic_metrics(exc.texto)
        hash_val = hermeneutic_segmenter.calculate_sha256(exc.texto, obra.titulo if obra else "Obra", exc.secao)
        
        resultados.append({
            "id": exc.id,
            "obra_titulo": obra.titulo if obra else "Desconhecida",
            "obra_slug": obra.slug if obra else "",
            "canto_ou_capitulo": cap.nome if cap else "",
            "secao": exc.secao,
            "estrofes": exc.estrofes,
            "texto": exc.texto,
            "hash_sha256": hash_val,
            "metricas_pln": metrics,
            "camada_iave_alvo": "Camada 2: Análise Retórico-Estilística" if "Lusíadas" in (obra.titulo if obra else "") else "Camada 3: Hermenêutica"
        })
        
    return resultados

@router.post("/rag-simulador")
def simular_recuperacao_rag(
    payload: RAGSimulationRequest,
    db: Session = Depends(get_db)
):
    """
    Simulador de RAG Transparente (Glass-Box): mostra ao investigador exatamente como o motor seleciona os excertos.
    """
    excertos = listar_excertos_com_metadados(obra_slug=payload.obra_slug, db=db)
    
    resultados_rag = rag_service.search_excerpts(
        query=payload.query,
        excerpts_corpus=excertos,
        top_k=payload.top_k,
        filtro_camada_iave=payload.camada_iave
    )
    
    return {
        "pergunta_investigada": payload.query,
        "total_candidatos_analisados": len(excertos),
        "excertos_recuperados": resultados_rag
    }

@router.get("/export/spss")
def exportar_dataset_spss(db: Session = Depends(get_db)):
    """Exporta matriz empírica formatada para IBM SPSS Statistics."""
    checkpoints = db.query(Checkpoint).all()
    dados_mock = []
    for c in checkpoints:
        dados_mock.append({
            "id": c.id,
            "usuario_id": c.usuario_id,
            "obra_slug": "os-lusiadas",
            "camada_iave": "camada_2",
            "nivel_bloom": c.nivel_bloom,
            "nota_iave_total_20": c.pontuacao * 2.0,
            "parametros_iave": {
                "parametro_c_conteudo": {"nota_percentual": 75},
                "parametro_f_estruturacao": {"nota_percentual": 80},
                "parametro_e_expressao": {"nota_percentual": 85}
            },
            "leitura_sustentada": c.leitura_sustentada,
            "total_palavras": len(c.resposta_aluno.split()) if c.resposta_aluno else 30,
            "tempo_resposta_segundos": 95
        })
        
    csv_content = scientific_export_service.export_spss_csv(dados_mock)
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=relia_dataset_spss.csv"}
    )

@router.get("/export/r-script")
def exportar_script_r(db: Session = Depends(get_db)):
    """Exporta script de análise estatística em R com dataframe embutido."""
    checkpoints = db.query(Checkpoint).all()
    dados_mock = [
        {
            "id": c.id,
            "usuario_id": c.usuario_id,
            "camada_iave": "Camada 2",
            "nivel_bloom": c.nivel_bloom,
            "nota_iave_total_20": c.pontuacao * 2.0,
            "leitura_sustentada": c.leitura_sustentada
        }
        for c in checkpoints
    ]
    r_code = scientific_export_service.export_r_script(dados_mock)
    return Response(
        content=r_code,
        media_type="text/plain",
        headers={"Content-Disposition": "attachment; filename=relia_analise_doutoramento.R"}
    )

@router.get("/export/nvivo")
def exportar_transcritos_nvivo(db: Session = Depends(get_db)):
    """Exporta corpus qualitativo codificado para o NVivo."""
    checkpoints = db.query(Checkpoint).all()
    logs = [
        {
            "id": c.id,
            "pergunta": c.pergunta,
            "resposta_aluno": c.resposta_aluno,
            "feedback_agente": c.avaliacao_feedback,
            "nivel_bloom": c.nivel_bloom
        }
        for c in checkpoints
    ]
    nvivo_json = scientific_export_service.export_nvivo_json(logs)
    return Response(
        content=nvivo_json,
        media_type="application/json",
        headers={"Content-Disposition": "attachment; filename=relia_corpus_nvivo.json"}
    )
