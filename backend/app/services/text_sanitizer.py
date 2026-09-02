"""
Sanitizador e Normalizador Filológico de Textos Literários
Remove cabeçalhos e rodapés de licenças (Project Gutenberg, etc.), corrige quebras de linha espúrias
e preserva a fidelidade ortográfica (arcaísmos e grafias quinhentistas/seiscentistas vs moderno).
"""

import re
from typing import Dict, Any, Tuple

GUTENBERG_START_MARKERS = [
    r"\*\*\* START OF THIS PROJECT GUTENBERG",
    r"\*\*\* START OF THE PROJECT GUTENBERG",
    r"\*\*\*START OF THE PROJECT GUTENBERG",
    r"Project Gutenberg's",
    r"The Project Gutenberg eBook",
    r"*** START OF",
]

GUTENBERG_END_MARKERS = [
    r"\*\*\* END OF THIS PROJECT GUTENBERG",
    r"\*\*\* END OF THE PROJECT GUTENBERG",
    r"\*\*\*END OF THE PROJECT GUTENBERG",
    r"End of the Project Gutenberg",
    r"End of Project Gutenberg",
    r"*** END OF",
]

class TextSanitizer:
    @staticmethod
    def strip_gutenberg_boilerplate(raw_text: str) -> str:
        """
        Remove os cabeçalhos de aviso legal e rodapés padrão do Project Gutenberg.
        """
        text = raw_text
        
        # Encontrar início real da obra
        for marker in GUTENBERG_START_MARKERS:
            match = re.search(marker, text, re.IGNORECASE)
            if match:
                # Pular a linha do marcador
                start_pos = match.end()
                newline_pos = text.find("\n", start_pos)
                if newline_pos != -1:
                    text = text[newline_pos + 1:]
                break
        
        # Encontrar final real da obra
        for marker in GUTENBERG_END_MARKERS:
            match = re.search(marker, text, re.IGNORECASE)
            if match:
                text = text[:match.start()]
                break
        
        return text.strip()

    @staticmethod
    def normalize_literary_text(raw_text: str, is_verse: bool = False) -> Tuple[str, Dict[str, Any]]:
        """
        Sanitiza o texto preservando a integridade métrica para versos ou o fluxo de parágrafos para prosa.
        """
        cleaned = TextSanitizer.strip_gutenberg_boilerplate(raw_text)
        
        # Normalizar quebras de linha Windows/Mac/Linux
        cleaned = cleaned.replace("\r\n", "\n").replace("\r", "\n")
        
        # Remover múltiplos espaços horizontais
        cleaned = re.sub(r"[ \t]+", " ", cleaned)
        
        # Detectar se o texto possui marcas ortográficas arcaicas
        marcas_arcaicas = [
            r"\bassi\b", r"\bhum\b", r"\bhuma\b", r"\bcousa\b", r"\bhe\b", 
            r"\bpella\b", r"\bpello\b", r"\bhonra\b", r"\blhe\b"
        ]
        
        count_arcaico = sum(len(re.findall(p, cleaned, re.IGNORECASE)) for p in marcas_arcaicas)
        tipo_ortografia = "arcaica_classica" if count_arcaico > 10 else "modernizada"
        
        if is_verse:
            # Em verso, não podemos colapsar quebras de linha simples
            # Mas removemos 3 ou mais quebras de linha consecutivas
            cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
        else:
            # Em prosa, parágrafos são separados por linhas duplas
            # Mas quebras de linha simples de OCR no meio de orações são juntadas
            paragrafos = cleaned.split("\n\n")
            paragrafos_ajustados = []
            for p in paragrafos:
                # Junta linhas dentro do mesmo parágrafo
                p_unido = " ".join(line.strip() for line in p.split("\n") if line.strip())
                if p_unido:
                    paragrafos_ajustados.append(p_unido)
            cleaned = "\n\n".join(paragrafos_ajustados)
        
        stats = {
            "total_caracteres": len(cleaned),
            "total_palavras": len(cleaned.split()),
            "tipo_ortografia": tipo_ortografia,
            "marcas_arcaicas_encontradas": count_arcaico,
            "is_verse": is_verse
        }
        
        return cleaned.strip(), stats

text_sanitizer = TextSanitizer()
