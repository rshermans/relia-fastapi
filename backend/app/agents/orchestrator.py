"""
Orquestrador Multi-Agente do RELIA 2.0
Integração das 3 Skills Agênticas com as 4 Camadas IAVE, RAG Transparente e Motor Multi-LLM.
"""

from typing import Dict, Any, List, Optional
from backend.app.skills.extrator_discursivo import extrator_discursivo_service
from backend.app.skills.formulador_socratico import formulador_socratico_service, CAMADAS_ESTUDO_IAVE
from backend.app.skills.avaliador_metacognitivo import avaliador_metacognitivo_service
from backend.app.agents.mcp_client import mcp_corpus_client
from backend.app.services.llm_service import llm_service
from backend.app.services.rag_service import rag_service

class ReliaAgentOrchestrator:
    """
    Orquestrador central de mediação leitora agêntica com suporte ao IAVE e Multi-LLM.
    """

    async def mediar_dialogo_socratico(
        self,
        mensagem_usuario: str,
        historico: List[Dict[str, str]],
        obra_slug: Optional[str] = None,
        canto_ou_capitulo: Optional[int] = None,
        secao: Optional[str] = None,
        nivel_bloom: str = "Entender",
        camada_iave_id: str = "camada_2",
        provider: Optional[str] = None,
        model: Optional[str] = None,
        api_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Orquestra a análise discursiva do excerto, formulação socrática em 4 camadas IAVE e inferência Multi-LLM.
        """
        # 1. Recuperação do Corpus via MCP / Base Local
        contexto_texto = ""
        analise_previa = ""
        obra_titulo = obra_slug or "Obra Literária"
        
        if obra_slug and canto_ou_capitulo:
            dados_excerto = mcp_corpus_client.obter_excerto(obra_slug, canto_ou_capitulo, secao)
            if "excertos" in dados_excerto and dados_excerto["excertos"]:
                exc = dados_excerto["excertos"][0]
                contexto_texto = exc.get("texto", "")
                analise_previa = exc.get("analise_retorica", "")
                obra_titulo = dados_excerto.get("obra", obra_slug)

        # 2. Execução da Skill 1: Extrator Discursivo
        analise_estilistica = extrator_discursivo_service.analisar_excerto(
            texto=contexto_texto or mensagem_usuario,
            analise_previa=analise_previa
        )

        # 3. Execução da Skill 2: Formulador Socrático (com Camada IAVE)
        pergunta_guia = formulador_socratico_service.gerar_pergunta_socratica(
            obra_titulo=obra_titulo,
            secao_titulo=secao or "Excerto em análise",
            excerto_texto=contexto_texto,
            nivel_bloom=nivel_bloom,
            camada_iave_id=camada_iave_id
        )

        # 4. Prompt Instrucional Alinhado aos Critérios IAVE e Pragmática da Leitura
        camada_nome = pergunta_guia.get("camada_iave", "Camada 2: Análise Retórico-Estilística")
        prompt_sistema = (
            f"Você é o Professor Literário Automatizado do RELIA 2.0, um mediador empático e especialista nos Exames Nacionais de Portugal (IAVE).\n"
            f"Você está atualmente a orientar o estudante na: [{camada_nome}].\n\n"
            f"Princípios Pragmático-Discursivos:\n"
            f"1. Jamais entregue a resposta pronta ou resumos banais que retirem a iniciativa interpretativa do aluno;\n"
            f"2. Conduza o raciocínio por perguntas abertas graduadas pela Taxonomia de Bloom ({nivel_bloom});\n"
            f"3. Incentive a identificação e interpretação do valor expressivo das figuras de estilo detetadas ({', '.join(analise_estilistica['figuras_de_estilo'][:3])});\n"
            f"4. Valorize as leituras fundamentadas com citações explícitas do excerto;\n"
            f"5. Responda em Português de Portugal culto, elegante e acolhedor."
        )

        contexto_completo = (
            f"Obra: {obra_titulo}\n"
            f"Passagem / Excerto:\n{contexto_texto}\n\n"
            f"Figuras de Estilo Detetadas: {', '.join(analise_estilistica['figuras_de_estilo'])}\n"
            f"Campos Lexicais: {', '.join(analise_estilistica['campos_lexicais'])}\n"
            f"Questão Socrática IAVE: {pergunta_guia['pergunta_socratica']}"
        )

        # 5. Geração da Réplica pelo Adaptador Universal Multi-LLM
        mensagens_completas = list(historico)
        mensagens_completas.append({"role": "user", "content": mensagem_usuario})

        resultado_llm = await llm_service.gerar_resposta_socratica(
            prompt_sistema=prompt_sistema,
            mensagens_historico=mensagens_completas,
            contexto_corpus=contexto_completo,
            nivel_bloom=nivel_bloom,
            camada_iave=camada_nome,
            provider=provider,
            model=model,
            api_key=api_key
        )

        return {
            "resposta": resultado_llm.get("content", ""),
            "provedor_utilizado": resultado_llm.get("provider", "local"),
            "modelo_utilizado": resultado_llm.get("model", "default"),
            "fallback_acionado": resultado_llm.get("fallback_triggered", False),
            "camada_iave": camada_nome,
            "camada_iave_id": camada_iave_id,
            "nivel_bloom": nivel_bloom,
            "analise_discursiva": analise_estilistica,
            "diretiva_socratica": pergunta_guia
        }

    def avaliar_resposta_iave(
        self,
        pergunta: str,
        resposta_aluno: str,
        excerto_referencia: Optional[str] = None,
        camada_iave_id: str = "camada_2",
        nivel_bloom: str = "Entender"
    ) -> Dict[str, Any]:
        """
        Executa a Skill 3: Avaliador Metacognitivo segundo os critérios IAVE (Parâmetros C, F, E).
        """
        return avaliador_metacognitivo_service.avaliar_resposta_iave(
            pergunta=pergunta,
            resposta_aluno=resposta_aluno,
            excerto_referencia=excerto_referencia,
            camada_iave_id=camada_iave_id,
            nivel_bloom=nivel_bloom
        )

    def avaliar_checkpoint_metacognitivo(
        self,
        pergunta: str,
        resposta_aluno: str,
        nivel_bloom: str = "Entender",
        criterios_referencia: Optional[List[str]] = None,
        resposta_modelo: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Avalia pedagogicamente uma resposta discursiva de checkpoint conectando à Skill 3 e convertendo para a escala do checkpoint.
        """
        resultado_iave = avaliador_metacognitivo_service.avaliar_resposta_iave(
            pergunta=pergunta,
            resposta_aluno=resposta_aluno,
            nivel_bloom=nivel_bloom
        )
        nota_20 = resultado_iave.get("nota_iave_total_20", 0.0)
        pontuacao_10 = round(nota_20 / 2.0, 1)

        return {
            "pontuacao": pontuacao_10,
            "nivel_bloom": nivel_bloom,
            "feedback_empatico": resultado_iave.get("feedback_empatico", ""),
            "pontos_fortes": resultado_iave.get("pontos_fortes", []),
            "lacunas_argumentativas": resultado_iave.get("lacunas_argumentativas", []),
            "leitura_sustentada": resultado_iave.get("leitura_sustentada", False),
            "sugestao_aprofundamento": resultado_iave.get("sugestao_aprofundamento", ""),
            "detalhes_iave": resultado_iave
        }

relia_orchestrator = ReliaAgentOrchestrator()

