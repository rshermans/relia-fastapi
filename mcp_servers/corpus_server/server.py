"""
Servidor MCP (Model Context Protocol) - Corpus Literário RELIA
Fornece ferramentas semânticas e de recuperação documental para agentes do ecossistema RELIA.
Obras Canónicas: Os Lusíadas (Luís de Camões), Sermão de Santo António aos Peixes (Padre António Vieira)
Itens de Exames Nacionais e Taxonomia de Bloom.
"""

import os
import json
from typing import List, Dict, Any, Optional
# Caminhos para dados do corpus
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA_DIR = os.path.join(BASE_DIR, "data", "seed_corpus")
OBRAS_FILE = os.path.join(DATA_DIR, "obras_canonicais.json")
EXAMES_FILE = os.path.join(DATA_DIR, "exames_nacionais.json")
BLOOM_FILE = os.path.join(DATA_DIR, "bloom_taxonomia.json")

# Inicialização do servidor FastMCP com fallback gracioso
try:
    from mcp.server.fastmcp import FastMCP
    mcp = FastMCP("RELIA Corpus & Literary Knowledge Server")
    tool_decorator = mcp.tool()
except ImportError:
    class DummyMCP:
        def tool(self):
            def decorator(func):
                return func
            return decorator
        def run(self):
            print("Servidor MCP em modo de ferramentas nativas locais.")
    mcp = DummyMCP()
    tool_decorator = mcp.tool()

def _load_json(file_path: str) -> Any:
    if not os.path.exists(file_path):
        return []
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

@tool_decorator
def list_available_works() -> List[Dict[str, Any]]:

    """Lista todas as obras canónicas disponíveis no corpus literário do RELIA."""
    obras = _load_json(OBRAS_FILE)
    return [
        {
            "slug": o.get("slug"),
            "titulo": o.get("titulo"),
            "autor": o.get("autor"),
            "epoca": o.get("epoca"),
            "genero": o.get("genero"),
            "descricao": o.get("descricao"),
            "total_capitulos": len(o.get("capitulos_ou_cantos", []))
        }
        for o in obras
    ]


@tool_decorator
def get_obra_excerpt(obra_slug: str, canto_ou_capitulo: int, secao: Optional[str] = None) -> Dict[str, Any]:
    """
    Recupera excertos específicos, estrofes e notas retórico-estilísticas de uma obra.
    
    Args:
        obra_slug: Slug da obra (ex: 'os-lusiadas', 'sermao-de-santo-antonio-aos-peixes')
        canto_ou_capitulo: Número do canto (Lusíadas) ou capítulo (Sermão)
        secao: Nome opcional da seção ou episódio (ex: 'O Gigante Adamastor', 'O Polvo e a Hipocrisia')
    """
    obras = _load_json(OBRAS_FILE)
    obra_match = next((o for o in obras if o.get("slug") == obra_slug), None)
    if not obra_match:
        return {"error": f"Obra com slug '{obra_slug}' não encontrada."}

    capitulos = obra_match.get("capitulos_ou_cantos", [])
    cap_match = next((c for c in capitulos if c.get("numero") == canto_ou_capitulo), None)
    if not cap_match:
        return {"error": f"Canto/Capítulo {canto_ou_capitulo} não encontrado para a obra '{obra_slug}'."}

    excertos = cap_match.get("excertos", [])
    if secao:
        excertos = [e for e in excertos if secao.lower() in e.get("secao", "").lower()]

    return {
        "obra": obra_match.get("titulo"),
        "autor": obra_match.get("autor"),
        "canto_ou_capitulo": cap_match.get("nome"),
        "total_excertos_encontrados": len(excertos),
        "excertos": excertos
    }


@tool_decorator
def search_corpus_annotations(query: str, obra_slug: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Pesquisa em todo o corpus literário por termos estilísticos, figuras de retórica, temas ou passagens.
    
    Args:
        query: Termo de busca textual ou estilístico (ex: 'Adamastor', 'hipocrisia', 'Fado', 'polvo')
        obra_slug: Filtro opcional por obra
    """
    obras = _load_json(OBRAS_FILE)
    results = []
    query_lower = query.lower()

    for obra in obras:
        if obra_slug and obra.get("slug") != obra_slug:
            continue
        for cap in obra.get("capitulos_ou_cantos", []):
            for exc in cap.get("excertos", []):
                texto = exc.get("texto", "").lower()
                secao = exc.get("secao", "").lower()
                analise = exc.get("analise_retorica", "").lower()
                if query_lower in texto or query_lower in secao or query_lower in analise:
                    results.append({
                        "obra": obra.get("titulo"),
                        "slug": obra.get("slug"),
                        "canto_ou_capitulo": cap.get("nome"),
                        "secao": exc.get("secao"),
                        "estrofes": exc.get("estrofes"),
                        "texto": exc.get("texto"),
                        "analise_retorica": exc.get("analise_retorica")
                    })
    return results


@tool_decorator
def get_national_exam_items(obra_slug: Optional[str] = None, bloom_level: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Recupera itens calibrados de Exames Nacionais de Português classificados pela Taxonomia de Bloom.
    
    Args:
        obra_slug: Filtro opcional por obra
        bloom_level: Nível de Bloom (ex: 'Lembrar', 'Entender', 'Aplicar', 'Analisar', 'Avaliar', 'Criar')
    """
    exames = _load_json(EXAMES_FILE)
    results = exames
    if obra_slug:
        results = [e for e in results if e.get("obra_slug") == obra_slug]
    if bloom_level:
        results = [e for e in results if e.get("nivel_bloom", "").lower() == bloom_level.lower()]
    return results


@tool_decorator
def get_bloom_taxonomy_matrix() -> Dict[str, Any]:
    """Retorna a matriz completa da Taxonomia de Bloom com objetivos, verbos operatórios e níveis cognitivos."""
    data = _load_json(BLOOM_FILE)
    return data


if __name__ == "__main__":
    mcp.run()
