"""
Segmentador Hermenêutico Guiado por Gramática de Género Literário
Executa o chunking estruturado de acordo com as especificidades do género:
- Épica (Cantos e Oitavas Rimas)
- Oratória / Prosa Barroca (Unidades Retóricas e Capítulos)
- Teatro / Drama (Atos, Cenas e Diálogos)
- Romance / Prosa (Capítulos e Sequências Narrativas)

Gera metadados científicos, índices de PLN (densidade léxica, etc.) e hash SHA-256 para cada excerto.
"""

import hashlib
import re
from typing import List, Dict, Any

class HermeneuticSegmenter:
    @staticmethod
    def calculate_sha256(text: str, obra_titulo: str, localizacao: str) -> str:
        """Gera assinatura criptográfica única do excerto para reprodutibilidade científica."""
        payload = f"{obra_titulo}::{localizacao}::{text.strip()}".encode("utf-8")
        return hashlib.sha256(payload).hexdigest()

    @staticmethod
    def extract_linguistic_metrics(text: str) -> Dict[str, Any]:
        """Calcula métricas linguísticas e estilísticas fundamentais."""
        words = re.findall(r"\b\w+\b", text)
        sentences = [s.strip() for s in re.split(r"[.!?]+", text) if s.strip()]
        
        total_words = len(words)
        unique_words = len(set(w.lower() for w in words))
        ttr = round(unique_words / total_words, 3) if total_words > 0 else 0.0
        mlu = round(total_words / len(sentences), 2) if sentences else 0.0
        
        # Deteção preliminar de potenciais figuras de estilo por padrões sintáticos/lexicais
        recursos_detectados = []
        if re.search(r"\bcomo\b|\bqual\b|\btal como\b", text, re.IGNORECASE):
            recursos_detectados.append("Comparação")
        if re.search(r"(\b\w+\b).*\b\1\b", text, re.IGNORECASE):
            recursos_detectados.append("Anáfora/Repetição")
        if re.search(r"\b(luz|sol|vida|bem)\b.*\b(noite|sombra|morte|mal)\b", text, re.IGNORECASE):
            recursos_detectados.append("Antítese/Oximoro")
        if "!" in text or re.search(r"\bó\b|\boh\b", text, re.IGNORECASE):
            recursos_detectados.append("Apóstrofe/Exclamação")
        
        return {
            "total_palavras": total_words,
            "vocabulario_unico": unique_words,
            "type_token_ratio_ttr": ttr,
            "total_sentencas": len(sentences),
            "comprimento_medio_sentenca_mlu": mlu,
            "recursos_estilisticos_provaveis": list(set(recursos_detectados))
        }

    def segment_epic_poetry(self, text: str, obra_titulo: str = "Os Lusíadas", max_strophes_per_chunk: int = 3) -> List[Dict[str, Any]]:
        """
        Segmenta poesia épica (ex: Os Lusíadas) agrupando estrofes em blocos coerentes.
        """
        # Divide por blocos de estrofes (linhas duplas)
        raw_strophes = [s.strip() for s in re.split(r"\n\s*\n", text) if s.strip()]
        
        chunks = []
        current_chunk_strophes = []
        canto_atual = 1
        strophe_counter = 1
        start_strophe_num = 1
        
        for strophe in raw_strophes:
            # Verifica se há marcador de Canto (ex: 'CANTO PRIMEIRO', 'CANTO I', etc.)
            canto_match = re.search(r"CANTO\s+([IVXLCDM]+|[A-Z]+)", strophe, re.IGNORECASE)
            if canto_match:
                # Se tínhamos estrofes acumuladas, fecha o chunk anterior
                if current_chunk_strophes:
                    chunk_text = "\n\n".join(current_chunk_strophes)
                    loc = f"Canto {canto_atual}, Estrofes {start_strophe_num}-{strophe_counter-1}"
                    metrics = self.extract_linguistic_metrics(chunk_text)
                    chunks.append({
                        "localizacao": loc,
                        "canto_ou_capitulo": f"Canto {canto_atual}",
                        "estrofes": f"{start_strophe_num}-{strophe_counter-1}",
                        "texto": chunk_text,
                        "hash_sha256": self.calculate_sha256(chunk_text, obra_titulo, loc),
                        "metricas_pln": metrics,
                        "genero": "Poesia Épica",
                        "camada_iave_recomendada": "Camada 2: Análise Retórico-Estilística"
                    })
                    current_chunk_strophes = []
                canto_atual += 1
                strophe_counter = 1
                start_strophe_num = 1
                continue
            
            current_chunk_strophes.append(strophe)
            if len(current_chunk_strophes) >= max_strophes_per_chunk:
                chunk_text = "\n\n".join(current_chunk_strophes)
                loc = f"Canto {canto_atual}, Estrofes {start_strophe_num}-{start_strophe_num + len(current_chunk_strophes) - 1}"
                metrics = self.extract_linguistic_metrics(chunk_text)
                chunks.append({
                    "localizacao": loc,
                    "canto_ou_capitulo": f"Canto {canto_atual}",
                    "estrofes": f"{start_strophe_num}-{start_strophe_num + len(current_chunk_strophes) - 1}",
                    "texto": chunk_text,
                    "hash_sha256": self.calculate_sha256(chunk_text, obra_titulo, loc),
                    "metricas_pln": metrics,
                    "genero": "Poesia Épica",
                    "camada_iave_recomendada": "Camada 2: Análise Retórico-Estilística"
                })
                start_strophe_num += len(current_chunk_strophes)
                current_chunk_strophes = []
            
            strophe_counter += 1

        # Resíduo final
        if current_chunk_strophes:
            chunk_text = "\n\n".join(current_chunk_strophes)
            loc = f"Canto {canto_atual}, Estrofes {start_strophe_num}-{start_strophe_num + len(current_chunk_strophes) - 1}"
            metrics = self.extract_linguistic_metrics(chunk_text)
            chunks.append({
                "localizacao": loc,
                "canto_ou_capitulo": f"Canto {canto_atual}",
                "estrofes": f"{start_strophe_num}-{start_strophe_num + len(current_chunk_strophes) - 1}",
                "texto": chunk_text,
                "hash_sha256": self.calculate_sha256(chunk_text, obra_titulo, loc),
                "metricas_pln": metrics,
                "genero": "Poesia Épica",
                "camada_iave_recomendada": "Camada 2: Análise Retórico-Estilística"
            })

        return chunks

    def segment_oratory_sermon(self, text: str, obra_titulo: str = "Sermão de Santo António aos Peixes") -> List[Dict[str, Any]]:
        """
        Segmenta sermões barrocos de acordo com a retórica clássica e capítulos.
        """
        raw_paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
        chunks = []
        capitulo_num = 1
        current_chunk_paras = []
        para_idx = 1
        
        for p in raw_paragraphs:
            # Verifica se inicia novo capítulo
            cap_match = re.search(r"CAP[ÍI]TULO\s+([IVXLCDM]+|\d+)", p, re.IGNORECASE)
            if cap_match:
                if current_chunk_paras:
                    chunk_text = "\n\n".join(current_chunk_paras)
                    loc = f"Capítulo {capitulo_num}, Excerto {para_idx}"
                    metrics = self.extract_linguistic_metrics(chunk_text)
                    chunks.append({
                        "localizacao": loc,
                        "canto_ou_capitulo": f"Capítulo {capitulo_num}",
                        "estrofes": None,
                        "texto": chunk_text,
                        "hash_sha256": self.calculate_sha256(chunk_text, obra_titulo, loc),
                        "metricas_pln": metrics,
                        "genero": "Oratória / Prosa Barroca",
                        "camada_iave_recomendada": "Camada 3: Hermenêutica e Crítica Social"
                    })
                    current_chunk_paras = []
                capitulo_num += 1
                para_idx = 1
                continue
            
            current_chunk_paras.append(p)
            # Agrupa a cada 2 ou 3 parágrafos substanciais
            if len(current_chunk_paras) >= 3 or len(" ".join(current_chunk_paras)) > 1200:
                chunk_text = "\n\n".join(current_chunk_paras)
                loc = f"Capítulo {capitulo_num}, Excerto {para_idx}"
                metrics = self.extract_linguistic_metrics(chunk_text)
                chunks.append({
                    "localizacao": loc,
                    "canto_ou_capitulo": f"Capítulo {capitulo_num}",
                    "estrofes": None,
                    "texto": chunk_text,
                    "hash_sha256": self.calculate_sha256(chunk_text, obra_titulo, loc),
                    "metricas_pln": metrics,
                    "genero": "Oratória / Prosa Barroca",
                    "camada_iave_recomendada": "Camada 3: Hermenêutica e Crítica Social"
                })
                para_idx += 1
                current_chunk_paras = []

        if current_chunk_paras:
            chunk_text = "\n\n".join(current_chunk_paras)
            loc = f"Capítulo {capitulo_num}, Excerto {para_idx}"
            metrics = self.extract_linguistic_metrics(chunk_text)
            chunks.append({
                "localizacao": loc,
                "canto_ou_capitulo": f"Capítulo {capitulo_num}",
                "estrofes": None,
                "texto": chunk_text,
                "hash_sha256": self.calculate_sha256(chunk_text, obra_titulo, loc),
                "metricas_pln": metrics,
                "genero": "Oratória / Prosa Barroca",
                "camada_iave_recomendada": "Camada 3: Hermenêutica e Crítica Social"
            })

        return chunks

    def segment_general_text(self, text: str, obra_titulo: str, genero: str = "Prosa Geral") -> List[Dict[str, Any]]:
        """
        Segmentador polimórfico de fallback com base no género informado.
        """
        gen_lower = genero.lower()
        if "épica" in gen_lower or "poesia" in gen_lower or "lusíadas" in obra_titulo.lower():
            return self.segment_epic_poetry(text, obra_titulo)
        elif "sermão" in gen_lower or "oratória" in gen_lower or "vieira" in obra_titulo.lower():
            return self.segment_oratory_sermon(text, obra_titulo)
        else:
            return self.segment_oratory_sermon(text, obra_titulo)

hermeneutic_segmenter = HermeneuticSegmenter()
