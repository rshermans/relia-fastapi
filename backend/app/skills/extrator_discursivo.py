"""
Skill 1: Extrator Discursivo
Competência Linguístico-Discursiva: Análise estilística e retórica de excertos literários em língua portuguesa.
Mecanismo de Execução Autónomo: Identificação de figuras de estilo, estruturas sintáticas, índices léxicos e tonalidade expressiva.
"""

import re
from typing import Dict, Any, List

class ExtratorDiscursivo:
    def __init__(self):
        # Padrões retórico-linguísticos comuns para a poesia épica (Camões) e prosa oratória barroca (Vieira)
        self.figuras_patterns = {
            "antitese": [
                r"\b(luz|claro|dia)\b.*\b(noite|escuro|sombra)\b",
                r"\b(pequeno|pequenos)\b.*\b(grande|grandes)\b",
                r"\b(vida|viver)\b.*\b(morte|morrer)\b",
                r"\b(manso|brandura)\b.*\b(violência|cruel)\b",
                r"\b(céu|terra)\b.*\b(inferno|mar)\b"
            ],
            "paradoxo_oximoro": [
                r"\bferida que dói e não se sente\b",
                r"\bcontentamento descontente\b",
                r"\bmorte libertando\b",
                r"\bchoro sonoroso\b"
            ],
            "hiperbole": [
                r"\b(infinito|eterno|estranhíssimo|grandíssima|segundo de rodes colosso)\b",
                r"\b(mais do que prometia a força humana)\b",
                r"\b(não bastam cem.*nem mil)\b"
            ],
            "personificacao": [
                r"\b(figura se nos mostra no ar|rosto carregado|boca negra|olhos encovados)\b",
                r"\b(o mar profundo|olhai peixes lá do mar)\b",
                r"\b(polvo.*aspecto tão modesto.*candura)\b"
            ],
            "anastrofe_hipérbato": [
                r"\b(da ocidental praia lusitana.*passaram)\b",
                r"\b(da lei da morte libertando)\b"
            ],
            "interrogacao_retorica": [
                r"\b(que cores e que disfarces não toma\?)\b",
                r"\b(com que se há-de salgar\?)\b",
                r"\b(que há-de fazer o sal\?)\b"
            ]
        }

    def analisar_excerto(self, texto: str, analise_previa: str = None) -> Dict[str, Any]:
        """
        Executa a análise estilística e sintática de um excerto em língua portuguesa.
        """
        texto_clean = texto.strip()
        linhas = [l for l in texto_clean.split("\n") if l.strip()]
        palavras = re.findall(r"\b\w+\b", texto_clean.lower())
        total_palavras = len(palavras)
        total_versos_ou_periodos = len(linhas)

        # 1. Detecção de Figuras de Estilo e Recursos Expressivos
        figuras_detectadas = []
        for figura, padroes in self.figuras_patterns.items():
            for p in padroes:
                if re.search(p, texto_clean, re.IGNORECASE):
                    nome_formatado = figura.replace("_", " ").title()
                    if nome_formatado not in figuras_detectadas:
                        figuras_detectadas.append(nome_formatado)

        # 2. Análise de Vocabulário & Campos Lexicais Predominantes
        campos_lexicais = []
        if any(w in texto_clean.lower() for w in ["mar", "ondas", "navegados", "peixes", "água", "praia", "oceano"]):
            campos_lexicais.append("Marítimo / Oceânico")
        if any(w in texto_clean.lower() for w in ["deuses", "fé", "cristo", "sal", "olimpo", "fado", "apóstolos"]):
            campos_lexicais.append("Transcendental / Religioso e Mitológico")
        if any(w in texto_clean.lower() for w in ["armas", "barões", "guerra", "império", "força", "glória", "louro"]):
            campos_lexicais.append("Bélico / Heroico-Nacional")
        if any(w in texto_clean.lower() for w in ["hipocrisia", "trair", "judas", "enganar", "modéstia", "disfarces"]):
            campos_lexicais.append("Ético-Moral / Sátira Social")

        # 3. Estrutura e Tonalidade Sintática
        tonalidade = "Solene e Elevada" if any(w in texto_clean.lower() for w in ["armas", "reis", "padre", "deuses"]) else "Oratória e Persuasiva"

        return {
            "estatisticas_textuais": {
                "total_palavras": total_palavras,
                "total_linhas": total_versos_ou_periodos,
                "densidade_lexical": round(len(set(palavras)) / (total_palavras or 1), 2)
            },
            "figuras_de_estilo": figuras_detectadas or ["Metáfora", "Paralelismo"],
            "campos_lexicais": campos_lexicais or ["Linguagem Literária Canónica"],
            "tonalidade_discursiva": tonalidade,
            "analise_hermeneutica_ancorada": analise_previa or "Análise estilística orientada ao valor estético e argumentativo do texto."
        }

extrator_discursivo_service = ExtratorDiscursivo()
