"""
Cliente MCP Integrado para o Backend RELIA
Permite a invocação direta ou via subprocesso das ferramentas expostas pelo Servidor de Corpus MCP.
"""

import os
import json
from typing import Dict, Any, List, Optional
from mcp_servers.corpus_server.server import (
    list_available_works,
    get_obra_excerpt,
    search_corpus_annotations,
    get_national_exam_items,
    get_bloom_taxonomy_matrix
)

class MCPCorpusClient:
    """Cliente em Python para comunicação com as ferramentas do Servidor MCP de Corpus."""

    @staticmethod
    def listar_obras() -> List[Dict[str, Any]]:
        return list_available_works()

    @staticmethod
    def obter_excerto(obra_slug: str, canto_ou_capitulo: int, secao: Optional[str] = None) -> Dict[str, Any]:
        return get_obra_excerpt(obra_slug=obra_slug, canto_ou_capitulo=canto_ou_capitulo, secao=secao)

    @staticmethod
    def pesquisar_anotacoes(query: str, obra_slug: Optional[str] = None) -> List[Dict[str, Any]]:
        return search_corpus_annotations(query=query, obra_slug=obra_slug)

    @staticmethod
    def obter_itens_exames(obra_slug: Optional[str] = None, bloom_level: Optional[str] = None) -> List[Dict[str, Any]]:
        return get_national_exam_items(obra_slug=obra_slug, bloom_level=bloom_level)

    @staticmethod
    def obter_matriz_bloom() -> Dict[str, Any]:
        return get_bloom_taxonomy_matrix()

mcp_corpus_client = MCPCorpusClient()
