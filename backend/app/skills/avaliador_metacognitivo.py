"""
Skill 3: Avaliador Metacognitivo
Competência Linguístico-Discursiva: Análise de respostas abertas dos alunos e feedback empático-formativo.
Mecanismo de Execução Autónomo: Avaliação segundo os parâmetros oficiais do IAVE:
- Parâmetro C (Conteúdo e Sustentação Textual)
- Parâmetro F (Estruturação, Coerência e Conectores)
- Parâmetro E (Correção Linguística e Morfossintaxe)
"""

import re
from typing import Dict, Any, List, Optional

class AvaliadorMetacognitivo:
    def avaliar_resposta_iave(
        self,
        pergunta: str,
        resposta_aluno: str,
        excerto_referencia: Optional[str] = None,
        camada_iave_id: str = "camada_2",
        nivel_bloom: str = "Entender"
    ) -> Dict[str, Any]:
        """
        Avalia pedagogicamente uma resposta discursiva aberta do leitor segundo a grelha IAVE.
        """
        resposta_limpa = resposta_aluno.strip()
        palavras = re.findall(r"\b\w+\b", resposta_limpa.lower())
        total_palavras = len(palavras)

        if total_palavras < 5:
            return {
                "nota_iave_total_20": 2.0,
                "parametros_iave": {
                    "parametro_c_conteudo": {"nota_percentual": 15, "descricao": "Resposta excessivamente breve, sem sustentação textual."},
                    "parametro_f_estruturacao": {"nota_percentual": 10, "descricao": "Ausência de estrutura argumentativa."},
                    "parametro_e_expressao": {"nota_percentual": 30, "descricao": "Texto insuficiente para avaliação sintática."}
                },
                "feedback_empatico": "Notamos a sua tentativa inicial, mas a resposta é demasiado breve para demonstrar a profundidade da sua leitura. Que tal desenvolver o raciocínio fundamentando-se no excerto?",
                "pontos_fortes": ["Manifestação inicial de interesse"],
                "lacunas_argumentativas": ["Falta de citação textual direta", "Desenvolvimento insuficiente da ideia"],
                "leitura_sustentada": False,
                "sugestao_aprofundamento": "Releia o excerto e cite uma palavra ou expressão que justifique a sua conclusão."
            }

        pontos_fortes = []
        lacunas = []

        # 1. Avaliação do Parâmetro F (Estruturação e Conectores Discursivos)
        conectores_argumentativos = [
            "porque", "visto que", "pois", "portanto", "contudo", "embora", 
            "ao passo que", "por conseguinte", "em contrapartida", "com efeito",
            "assim", "além disso", "deste modo", "evidencia", "simboliza", "demonstra"
        ]
        conectores_presentes = [c for c in conectores_argumentativos if c in resposta_limpa.lower()]
        
        score_f = 40
        if len(conectores_presentes) >= 1:
            score_f += 30
            pontos_fortes.append(f"Uso de marcadores discursivos ({', '.join(conectores_presentes[:3])}).")
        if len(conectores_presentes) >= 3:
            score_f += 20
        if total_palavras >= 30:
            score_f += 10
        score_f = min(100, score_f)

        # 2. Avaliação do Parâmetro C (Conteúdo e Sustentação Textual)
        termos_literarios = [
            "camões", "vieira", "adamastor", "peixes", "polvo", "sal", "deuses", 
            "lusíadas", "metáfora", "alegoria", "barroco", "épico", "inês de castro",
            "restelo", "roncadores", "pegadores", "sátira", "ironia", "antítese"
        ]
        mencoes_literarias = [p for p in termos_literarios if p in resposta_limpa.lower()]
        
        score_c = 40
        if mencoes_literarias:
            score_c += 35
            pontos_fortes.append(f"Mobilização de conceitos-chave ({', '.join(mencoes_literarias)}).")
        else:
            lacunas.append("Tente citar termos do excerto para comprovar a sua interpretação.")
            
        # Verifica se há aspas (citações textuais)
        if '"' in resposta_aluno or '«' in resposta_aluno or "'" in resposta_aluno:
            score_c += 25
            pontos_fortes.append("Presença de citações textuais diretas do excerto.")
        score_c = min(100, score_c)

        # 3. Avaliação do Parâmetro E (Expressão e Correção Linguística)
        score_e = 80 # Padrão
        # Detecção de potenciais erros grosseiros ou informalidades
        if re.search(r"\b(pq|tb|vc|pra|tá)\b", resposta_limpa.lower()):
            score_e -= 30
            lacunas.append("Evite abreviaturas e linguagem coloquial; privilegie o registo formal de língua.")
        if total_palavras >= 20 and not re.search(r"[.!?]", resposta_aluno):
            score_e -= 15
            lacunas.append("Utilize pontuação adequada para delimitar as frases e parágrafos.")

        # Cálculo da Nota Global IAVE (escala 0 a 20 valores)
        # Ponderação IAVE clássica: C = 60%, F = 20%, E = 20%
        nota_ponderada_100 = (score_c * 0.60) + (score_f * 0.20) + (score_e * 0.20)
        nota_20 = round((nota_ponderada_100 / 100) * 20, 1)
        leitura_sustentada = nota_20 >= 12.0

        # Feedback dialógico empático
        if nota_20 >= 17.0:
            feedback = "Excelente resposta! O seu texto demonstra maturidade crítica, rigor conceitual e perfeita articulação com o excerto lido, correspondendo aos níveis de excelência dos critérios IAVE."
        elif nota_20 >= 13.0:
            feedback = "Muito boa leitura! A interpretação é consistente e bem direcionada. Para aperfeiçoar ainda mais, aprofunde a análise dos efeitos de sentido gerados pelos recursos expressivos identificados."
        elif nota_20 >= 9.5:
            feedback = "Resposta positiva e com ideias válidas. Para consolidar o seu argumento, assegure uma maior sustentação textual através de transcrições comentadas do excerto."
        else:
            feedback = "Identificámos o seu esforço de reflexão, mas a resposta beneficiaria de um maior detalhamento das ideias e de referências explícitas ao texto da obra."

        return {
            "nota_iave_total_20": nota_20,
            "parametros_iave": {
                "parametro_c_conteudo": {
                    "nota_percentual": score_c,
                    "descricao": "Rigor temático e fundamentação nos elementos do excerto."
                },
                "parametro_f_estruturacao": {
                    "nota_percentual": score_f,
                    "descricao": "Coesão, coerência textual e uso de articuladores discursivos."
                },
                "parametro_e_expressao": {
                    "nota_percentual": score_e,
                    "descricao": "Correção sintática, registo de língua e precisão vocabular."
                }
            },
            "feedback_empatico": feedback,
            "pontos_fortes": pontos_fortes or ["Compreensão global do excerto"],
            "lacunas_argumentativas": lacunas or ["Aprofundamento da sustentação crítica"],
            "leitura_sustentada": leitura_sustentada,
            "camada_iave_id": camada_iave_id,
            "sugestao_aprofundamento": "Como você contraporia a sua resposta à perspectiva de um leitor contemporâneo à época da obra?"
        }

avaliador_metacognitivo_service = AvaliadorMetacognitivo()
