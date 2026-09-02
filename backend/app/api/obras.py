from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

from backend.app.database.session import get_db
from backend.app.database.models import Obra, CapituloOuCanto, Excerto
from backend.app.schemas.schemas import ObraResponse, CapituloResponse, ExcertoResponse
from backend.app.agents.mcp_client import mcp_corpus_client
from backend.app.services.gutenberg_service import gutenberg_service
from backend.app.services.google_books_service import google_books_service
from backend.app.services.hermeneutic_segmenter import hermeneutic_segmenter
from backend.app.services.text_sanitizer import text_sanitizer

router = APIRouter(prefix="/obras", tags=["Obras & Corpus Literário"])

class IngestGutenbergRequest(BaseModel):
    gutenberg_id: int
    titulo: str
    autor: str
    genero: str = "Poesia Épica"
    txt_url: str
    epoca: Optional[str] = "Quinhentismo / Renascimento"

class IngestTextRequest(BaseModel):
    titulo: str
    autor: str
    genero: str = "Poesia Épica"
    epoca: Optional[str] = "Clássico"
    texto_integral: str
    is_verse: bool = False

@router.get("", response_model=List[ObraResponse])
def listar_obras(db: Session = Depends(get_db)):
    obras = db.query(Obra).all()
    return obras

@router.get("/search-gutenberg")
async def buscar_no_gutenberg(query: str = Query(..., description="Autor ou título da obra")):
    """Pesquisa obras em domínio público no Project Gutenberg (via Gutendex)."""
    return await gutenberg_service.search_books(query=query, languages="pt")

@router.get("/search-google-books")
async def buscar_no_google_books(query: str = Query(..., description="Termo de pesquisa")):
    """Pesquisa obras e edições no Google Books API."""
    return await google_books_service.search_volumes(query=query, lang_restrict="pt")

@router.post("/ingest-gutenberg")
async def ingerir_obra_gutenberg(payload: IngestGutenbergRequest, db: Session = Depends(get_db)):
    """
    Descarrega a obra do Gutenberg, sanitiza paratextos, aplica o segmentador hermenêutico e persiste os excertos.
    """
    is_verse = "épica" in payload.genero.lower() or "poesia" in payload.genero.lower()
    fetch_res = await gutenberg_service.fetch_full_text(payload.txt_url, is_verse=is_verse)
    cleaned_text = fetch_res["cleaned_text"]
    
    # Criar registro da obra
    slug = payload.titulo.lower().replace(" ", "-").replace("ã", "a").replace("ç", "c").replace("õ", "o")
    existing = db.query(Obra).filter(Obra.slug == slug).first()
    if existing:
        obra = existing
    else:
        obra = Obra(
            slug=slug,
            titulo=payload.titulo,
            autor=payload.autor,
            genero=payload.genero,
            epoca=payload.epoca,
            descricao=f"Obra importada do Project Gutenberg (ID: {payload.gutenberg_id}). Estatísticas: {fetch_res['stats']['total_palavras']} palavras."
        )
        db.add(obra)
        db.commit()
        db.refresh(obra)

    # Executar segmentador hermenêutico
    chunks = hermeneutic_segmenter.segment_general_text(cleaned_text, payload.titulo, payload.genero)
    
    # Criar ou reutilizar capítulos e adicionar excertos
    cap_map = {}
    for ch in chunks:
        canto_nome = ch["canto_ou_capitulo"]
        if canto_nome not in cap_map:
            cap_obj = db.query(CapituloOuCanto).filter(CapituloOuCanto.obra_id == obra.id, CapituloOuCanto.nome == canto_nome).first()
            if not cap_obj:
                cap_obj = CapituloOuCanto(obra_id=obra.id, numero=len(cap_map) + 1, nome=canto_nome)
                db.add(cap_obj)
                db.commit()
                db.refresh(cap_obj)
            cap_map[canto_nome] = cap_obj
        
        cap_ref = cap_map[canto_nome]
        
        # Inserir Excerto
        exc_obj = Excerto(
            capitulo_id=cap_ref.id,
            secao=ch["localizacao"],
            estrofes=ch.get("estrofes"),
            texto=ch["texto"],
            analise_retorica=f"Figuras: {', '.join(ch['metricas_pln']['recursos_estilisticos_provaveis'])}. Hash SHA-256: {ch['hash_sha256']}"
        )
        db.add(exc_obj)

    db.commit()
    return {
        "status": "success",
        "obra_id": obra.id,
        "slug": obra.slug,
        "titulo": obra.titulo,
        "total_excertos_gerados": len(chunks),
        "estatisticas_sanitizacao": fetch_res["stats"],
        "amostra_primeiro_excerto": chunks[0] if chunks else None
    }

@router.post("/ingest-text")
def ingerir_texto_manual(payload: IngestTextRequest, db: Session = Depends(get_db)):
    """
    Ingestão direta de texto inserido manualmente com sanitização e segmentação por género.
    """
    cleaned_text, stats = text_sanitizer.normalize_literary_text(payload.texto_integral, is_verse=payload.is_verse)
    slug = payload.titulo.lower().replace(" ", "-").replace("ã", "a").replace("ç", "c").replace("õ", "o")
    
    obra = db.query(Obra).filter(Obra.slug == slug).first()
    if not obra:
        obra = Obra(
            slug=slug,
            titulo=payload.titulo,
            autor=payload.autor,
            genero=payload.genero,
            epoca=payload.epoca,
            descricao=f"Obra inserida diretamente pelo utilizador/professor. Estatísticas: {stats['total_palavras']} palavras."
        )
        db.add(obra)
        db.commit()
        db.refresh(obra)

    chunks = hermeneutic_segmenter.segment_general_text(cleaned_text, payload.titulo, payload.genero)
    
    cap = CapituloOuCanto(obra_id=obra.id, numero=1, nome="Secção Principal")
    db.add(cap)
    db.commit()
    db.refresh(cap)

    for ch in chunks:
        exc_obj = Excerto(
            capitulo_id=cap.id,
            secao=ch["localizacao"],
            estrofes=ch.get("estrofes"),
            texto=ch["texto"],
            analise_retorica=f"Figuras: {', '.join(ch['metricas_pln']['recursos_estilisticos_provaveis'])}. Hash: {ch['hash_sha256']}"
        )
        db.add(exc_obj)

    db.commit()
    return {
        "status": "success",
        "obra_id": obra.id,
        "slug": obra.slug,
        "total_excertos_gerados": len(chunks),
        "estatisticas_sanitizacao": stats
    }

# ─── Endpoints MCP Corpus (integração com ferramentas de corpus literário) ────

@router.get("/mcp/busca")
def busca_mcp_corpus(query: str = Query(..., description="Termo de pesquisa no corpus")):
    """Pesquisa anotações e excertos no corpus MCP por palavra-chave."""
    resultados = mcp_corpus_client.pesquisar_anotacoes(query=query)
    return {"query": query, "total_resultados": len(resultados), "resultados": resultados}

@router.get("/mcp/exames")
def listar_itens_exames():
    """Retorna itens de exame IAVE disponíveis no corpus MCP."""
    itens = mcp_corpus_client.obter_itens_exames()
    return {"total_itens": len(itens), "itens": itens}

@router.get("/mcp/bloom-matriz")
def obter_matriz_bloom():
    """Retorna a matriz de Bloom aplicável às obras do corpus."""
    return mcp_corpus_client.obter_matriz_bloom()

@router.get("/{slug}", response_model=ObraResponse)
def obter_obra_por_slug(slug: str, db: Session = Depends(get_db)):
    obra = db.query(Obra).filter(Obra.slug == slug).first()
    if not obra:
        raise HTTPException(status_code=404, detail="Obra literária não encontrada.")
    return obra

@router.get("/{slug}/capitulos", response_model=List[CapituloResponse])
def listar_capitulos(slug: str, db: Session = Depends(get_db)):
    obra = db.query(Obra).filter(Obra.slug == slug).first()
    if not obra:
        raise HTTPException(status_code=404, detail="Obra literária não encontrada.")
    return obra.capitulos
