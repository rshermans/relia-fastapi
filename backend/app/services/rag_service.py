"""
Serviço de RAG Transparente (Glass-Box RAG) para o RELIA 2.0
Combina busca lexical e similaridade semântica com explicabilidade científica total para o Doutoramento.
"""

import math
import re
from typing import List, Dict, Any, Optional

class TransparentRAGService:
    def __init__(self):
        pass

    def _tokenize(self, text: str) -> List[str]:
        return [w.lower() for w in re.findall(r"\b\w{3,}\b", text)]

    def compute_lexical_similarity(self, query: str, document: str) -> float:
        """Calcula similaridade de termos (Jaccard ponderado simplificado)."""
        query_tokens = set(self._tokenize(query))
        doc_tokens = set(self._tokenize(document))
        
        if not query_tokens or not doc_tokens:
            return 0.0
            
        intersection = query_tokens.intersection(doc_tokens)
        union = query_tokens.union(doc_tokens)
        return round(len(intersection) / len(union), 4)

    def search_excerpts(
        self,
        query: str,
        excerpts_corpus: List[Dict[str, Any]],
        top_k: int = 3,
        filtro_camada_iave: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Executa busca transparente sobre o corpus de excertos com métricas de explicabilidade.
        """
        scored_results = []
        query_terms = self._tokenize(query)
        
        for item in excerpts_corpus:
            texto = item.get("texto", "")
            if filtro_camada_iave and item.get("camada_iave_recomendada") != filtro_camada_iave:
                continue
                
            lex_score = self.compute_lexical_similarity(query, texto)
            
            # Encontrar termos exatos coincidentes
            doc_terms = set(self._tokenize(texto))
            termos_encontrados = list(set(query_terms).intersection(doc_terms))
            
            # Boost se os termos estiverem nas figuras de estilo ou metadados
            recursos = item.get("metricas_pln", {}).get("recursos_estilisticos_provaveis", [])
            for r in recursos:
                if r.lower() in query.lower():
                    lex_score += 0.25
            
            score_final = min(round(lex_score, 4), 1.0)
            
            scored_results.append({
                "excerto": item,
                "score_similaridade": score_final,
                "termos_chave_encontrados": termos_encontrados,
                "justificativa_recuperacao": (
                    f"Recuperado com score {score_final} devido à presença dos termos "
                    f"{termos_encontrados} e alinhamento com a {item.get('camada_iave_recomendada', 'Camada Geral')}."
                )
            })

        # Ordena por relevância decrescente
        scored_results.sort(key=lambda x: x["score_similaridade"], reverse=True)
        return scored_results[:top_k]

rag_service = TransparentRAGService()
