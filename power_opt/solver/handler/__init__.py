"""
Pacote `handler`

Contém módulos auxiliares para gerenciamento de configuração, extração de resultados,
depuração, visualização e exportação de saídas do modelo de otimização.

Autor: Giovani Santiago Junqueira
"""

__author__ = "Giovani Santiago Junqueira"

# Configurações do sistema
from .config_handler import extrair_configuracoes, aplicar_configuracoes

# Resultados reais do modelo
from .result_handler import extrair_resultados, salvar_resultados_em_csv

# Depuração e análise interna
from .debug_handler import (
    extrair_debug,
    debug_geracao,
    debug_objetivo,
    debug_perda_linha,
    debug_balanco_barras,
)

# Variáveis duais
from .dual_handler import (
    extrair_duais_em_dataframe,
    exportar_duais_csv,
    exportar_duais_csv_acumulado,
    imprimir_duais,
)

from .output_handler import exportar_saida

from .plot_handler import (
    plot_all, plot_deficit, plot_fluxo, plot_geracao, plot_perda,
    plot_n_menos_1_viabilidade, plot_delta_vs_fob, plot_delta_vs_fob_comparacao
)

__all__ = [
    # Configurações
    "extrair_configuracoes", "aplicar_configuracoes",

    # Resultados
    "extrair_resultados", "salvar_resultados_em_csv",

    # Duais
    "extrair_duais_em_dataframe", "exportar_duais_csv",
    "exportar_duais_csv_acumulado", "imprimir_duais",

    # Depuração
    "extrair_debug", "debug_perda_linha", "debug_geracao",
    "debug_objetivo", "debug_balanco_barras",

    # Exportação geral
    "exportar_saida",

    # Gráficos
    "plot_all", "plot_deficit", "plot_fluxo", "plot_geracao", "plot_perda",
    "plot_n_menos_1_viabilidade", "plot_delta_vs_fob", "plot_delta_vs_fob_comparacao"
]
