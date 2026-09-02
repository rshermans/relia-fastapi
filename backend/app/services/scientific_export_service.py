"""
Serviço de Exportação Científica para Doutoramento / Investigação Empírica
Gera datasets formatados para SPSS (.csv com dicionário de variáveis codificadas),
R (Script R com DataFrames) e NVivo (JSON/XML com nós temáticos e transcrições anotadas).
"""

import io
import csv
import json
from typing import List, Dict, Any

class ScientificExportService:
    @staticmethod
    def export_spss_csv(checkpoints: List[Dict[str, Any]]) -> str:
        """
        Exporta a matriz de dados empíricos pronta para importação no IBM SPSS Statistics.
        """
        output = io.StringIO()
        writer = csv.writer(output, delimiter=";")
        
        # Cabeçalhos com nomes padronizados para SPSS (<= 8/12 caracteres sem espaços)
        headers = [
            "id_check", "id_aluno", "obra_slug", "camada_iave", "bloom_level",
            "nota_iave_20", "score_param_c", "score_param_f", "score_param_e",
            "sustentada", "total_palavras", "tempo_resp_s"
        ]
        writer.writerow(headers)
        
        for c in checkpoints:
            writer.writerow([
                c.get("id", 1),
                c.get("usuario_id", 101),
                c.get("obra_slug", "os-lusiadas"),
                c.get("camada_iave", "camada_2"),
                c.get("nivel_bloom", "Entender"),
                c.get("nota_iave_total_20", 14.5),
                c.get("parametros_iave", {}).get("parametro_c_conteudo", {}).get("nota_percentual", 75),
                c.get("parametros_iave", {}).get("parametro_f_estruturacao", {}).get("nota_percentual", 80),
                c.get("parametros_iave", {}).get("parametro_e_expressao", {}).get("nota_percentual", 85),
                1 if c.get("leitura_sustentada", True) else 0,
                c.get("total_palavras", 45),
                c.get("tempo_resposta_segundos", 120)
            ])
            
        return output.getvalue()

    @staticmethod
    def export_r_script(checkpoints: List[Dict[str, Any]]) -> str:
        """
        Gera um script R com o data.frame embutido e comandos de estatística descritiva e testes de hipóteses.
        """
        json_data = json.dumps(checkpoints, ensure_ascii=False, indent=2)
        r_code = f"""# ==============================================================================
# PROJETO RELIA 2.0 - SCRIPT DE ANÁLISE ESTATÍSTICA DO DOUTORAMENTO (R)
# CEHUM / Universidade do Minho / FCT
# ==============================================================================

library(jsonlite)
library(ggplot2)
library(dplyr)

# 1. Carregar Corpus Empírico
json_raw <- '{json_data}'
dados_relia <- fromJSON(json_raw)

# 2. Estatística Descritiva da Avaliação IAVE
cat("--- ESTATÍSTICA DESCRITIVA (NOTAS IAVE / 20) ---\\n")
print(summary(dados_relia$nota_iave_total_20))

# 3. Análise por Camada de Estudo
media_por_camada <- dados_relia %>%
  group_by(camada_iave) %>%
  summarise(
    Media_Nota = mean(nota_iave_total_20, na.rm = TRUE),
    DP_Nota = sd(nota_iave_total_20, na.rm = TRUE),
    N = n()
  )
print(media_por_camada)

# 4. Gráfico de Boxplot / Distribuição com ggplot2
# ggplot(dados_relia, aes(x = camada_iave, y = nota_iave_total_20, fill = camada_iave)) +
#   geom_boxplot(alpha = 0.7) +
#   geom_jitter(width = 0.2, alpha = 0.5) +
#   theme_minimal() +
#   labs(title = "Distribuição do Desempenho por Camada de Estudo IAVE",
#        x = "Camada Pedagógica", y = "Nota IAVE (0-20)")
"""
        return r_code

    @staticmethod
    def export_nvivo_json(chat_logs: List[Dict[str, Any]]) -> str:
        """
        Exporta transcrições codificadas com metadados para análise qualitativa de conteúdo no NVivo.
        """
        nvivo_structure = {
            "projeto": "RELIA_2_0_PhD_CEHUM",
            "unidade_analise": "Dialogos_Socraticos_Alunos",
            "total_registos": len(chat_logs),
            "nos_tematicos_predefinidos": [
                "Descodificacao_Literal",
                "Analise_Estilistica_Retorica",
                "Hermeneutica_e_Critica_Social",
                "Argumentacao_Padrao_IAVE",
                "Feedback_Empatico_Recebido"
            ],
            "documentos": chat_logs
        }
        return json.dumps(nvivo_structure, ensure_ascii=False, indent=2)

scientific_export_service = ScientificExportService()
