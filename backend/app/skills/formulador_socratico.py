"""
Skill 2: Formulador Socrático
Competência Linguístico-Discursiva: Geração de perguntas interpretativas graduadas pela Taxonomia de Bloom
e estruturadas nas 4 Camadas de Estudo Literário segundo os padrões do IAVE (Exames Nacionais de Português).
"""

from typing import Dict, Any, List, Optional

CAMADAS_ESTUDO_IAVE = {
    "camada_1": {
        "nome": "Camada 1: Descodificação Literal e Estrutural",
        "foco": "Compreensão semântica imediata, vocabulário de época, localização na obra e identificação do sujeito poético/narrador.",
        "tipo_iave": "Itens de Seleção e Enquadramento Estrutural"
    },
    "camada_2": {
        "nome": "Camada 2: Análise Retórico-Estilística e Simbólica",
        "foco": "Identificação e valor expressivo dos recursos de estilo, pontuação e estruturas sintáticas.",
        "tipo_iave": "Grupo I - Itens de Resposta Restrita (Análise Formal)"
    },
    "camada_3": {
        "nome": "Camada 3: Hermenêutica, Contexto e Crítica Ideológica",
        "foco": "Interpretação da crítica social, do providencialismo, da alegoria e dos valores ético-filosóficos.",
        "tipo_iave": "Grupo I - Itens de Resposta Extensa / Interpretação Global"
    },
    "camada_4": {
        "nome": "Camada 4: Escrita Argumentativa e Síntese IAVE",
        "foco": "Produção de síntese crítica fundamentada no excerto, orientada pelos critérios dos Parâmetros C, F e E do IAVE.",
        "tipo_iave": "Grupo I (Síntese) e Grupo III (Ensaio Argumentativo)"
    }
}

class FormuladorSocratico:
    def __init__(self):
        self.bloom_verbos = {
            "Lembrar": ["identifique", "reconheça", "liste", "cite", "mencione"],
            "Entender": ["explique", "parafraseie", "resuma", "interprete", "descreva"],
            "Aplicar": ["relacione", "exemplifique", "demonstre", "aplique", "ilustre"],
            "Analisar": ["analise", "compare", "diferencie", "desconstrua", "evidencie"],
            "Avaliar": ["avalie", "julgue", "justifique", "critique", "pondere"],
            "Criar": ["elabore", "proponha", "formule", "reinterprete", "reconstrua"]
        }

    def gerar_pergunta_socratica(
        self,
        obra_titulo: str,
        secao_titulo: str,
        excerto_texto: str,
        nivel_bloom: str = "Entender",
        camada_iave_id: str = "camada_2",
        contexto_exame: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Gera uma questão socrática aberta articulada com a camada de estudo IAVE e o nível Bloom.
        """
        nivel = nivel_bloom.capitalize() if nivel_bloom.capitalize() in self.bloom_verbos else "Entender"
        camada_info = CAMADAS_ESTUDO_IAVE.get(camada_iave_id, CAMADAS_ESTUDO_IAVE["camada_2"])

        templates_camadas = {
            "camada_1": (
                f"Tendo por base a passagem de '{secao_titulo}' ({obra_titulo}), identifique quem são os interlocutores / "
                f"figuras centrais e descodifique o sentido das expressões e vocabulário arcaico mais relevantes."
            ),
            "camada_2": (
                f"No excerto de '{secao_titulo}', analise a funcionalidade expressiva dos recursos de estilo "
                f"(figuras retóricas e métrica/sintaxe) empregues pelo autor para intensificar a mensagem do texto."
            ),
            "camada_3": (
                f"A partir da leitura de '{secao_titulo}', interprete a crítica social, a dimensão moral ou a visão de mundo "
                f"veiculada pelo autor, relacionando-a com o contexto de produção da obra."
            ),
            "camada_4": (
                f"Num texto bem estruturado de 80 a 120 palavras (padrão Grupo I do IAVE), sustente com citações do excerto de '{secao_titulo}' "
                f"de que forma a passagem reflete uma tensão universal da condição humana."
            )
        }

        pergunta = templates_camadas.get(camada_iave_id, templates_camadas["camada_2"])

        system_prompt = (
            f"Você é o Agente Formulador Socrático do RELIA 2.0, um professor de literatura especialista nos Exames Nacionais de Portugal (IAVE).\n"
            f"Sua missão é conduzir o aluno pela '{camada_info['nome']}' (Foco: {camada_info['foco']}).\n"
            f"Nível cognitivo: {nivel}.\n"
            f"Regra de ouro: Nunca dê a resposta pronta. Formule perguntas empáticas, instigantes e que exijam citação textual."
        )

        return {
            "nivel_bloom": nivel,
            "camada_iave": camada_info["nome"],
            "camada_iave_id": camada_iave_id,
            "alinhamento_iave": camada_info["tipo_iave"],
            "pergunta_socratica": pergunta,
            "prompt_sistema_agente": system_prompt,
            "ancoragem_corpus": {
                "obra": obra_titulo,
                "secao": secao_titulo,
                "contexto_adicional": contexto_exame or "Item canónico alinhado ao 10º-12º ano."
            }
        }

formulador_socratico_service = FormuladorSocratico()
