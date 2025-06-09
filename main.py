"""
Script principal para execução de experimentos de otimização do sistema elétrico.
Executa o modelo para diferentes valores de delta e configurações, armazena e exporta os resultados.

Autor: Giovani Santiago Junqueira
"""

import time
import pandas as pd
from power_opt.experiments import simular_delta, simular_n_menos_1
from power_opt.utils import (limpar_diretorio, limpar_cache_py, preparar_df,
                             preparar_n_menos_1,
                            #  preparar_dados_graficos
)

from power_opt.solver.handler import (
    salvar_resultados_em_csv,
    # plot_all,
    plot_delta_vs_fob,
    plot_delta_vs_fob_comparacao,
    plot_n_menos_1_viabilidade
)

def main():
    """
    Função principal para configurar e executar os experimentos de otimização.
    Salva os resultados em arquivos CSV e gera gráficos.
    """
    inicio_t = time.time()
    json_path = "data/dados_base.json"
    deltas = [round(0.01 * i, 2) for i in range(0, 101)]
    # deltas = [1]
    config_base_com_perda = {
        "solver_name": "glpk", # "highs",
        "deficit": True, # checar somente deficit (deu erro)
        "transporte": True,
        "fluxo_dc": True,
        "perdas": True,
        "rampa": True,
        "emissao": True
    }

    config_base_sem_perda = config_base_com_perda.copy()
    config_base_sem_perda["perdas"] = False
    config_n_menos_1 = config_base_com_perda.copy()
    config_n_menos_1["fluxo_dc"] = False
    simulacoes = []
    df_com_perda, tempo_com_perda = simular_delta(json_path, deltas, config_base_com_perda)
    simulacoes.append(df_com_perda)
    df_sem_perda, tempo_sem_perda = simular_delta(json_path, deltas, config_base_sem_perda)
    simulacoes.append(df_sem_perda)
    n_menos_1 = simular_n_menos_1(json_path, config_n_menos_1)

    salvar_resultados_em_csv(simulacoes, "results/csv/simulacoes.csv")
    salvar_resultados_em_csv(df_com_perda, "results/csv/resultados_com_perda.csv")
    salvar_resultados_em_csv(df_sem_perda, "results/csv/resultados_sem_perda.csv")
    print("✅ Resultados salvos em 'results/csv/'")
    fim_t = time.time()

    # Geração de gráficos
    fob_com_perda = preparar_df(pd.concat(df_com_perda, ignore_index=True))
    fob_sem_perda = preparar_df(pd.concat(df_sem_perda, ignore_index=True))
    plot_delta_vs_fob(fob_com_perda, com_perda=True, nome_arquivo="results/figs/fob_com_perda.png")
    plot_delta_vs_fob(fob_sem_perda, com_perda=False, nome_arquivo="results/figs/fob_sem_perda.png")
    plot_delta_vs_fob_comparacao(fob_sem_perda, fob_com_perda)
    df_n1 = preparar_n_menos_1(n_menos_1)
    plot_n_menos_1_viabilidade(df_n1)

    print(
        f"⏱️ Tempo total das {2 * len(deltas)} simulações: {(fim_t - inicio_t):.2f} segundos")
    print(
        f"⏱️ Tempo médio com perdas: {tempo_com_perda:.2f} s | sem perdas: {tempo_sem_perda:.2f} s")

    # df_geracao, df_fluxo, df_deficit, df_perda = preparar_dados_graficos(df_com_perda)
    # plot_all(df_geracao, df_fluxo, df_deficit, df_perda, 'results/figs')

if __name__ == "__main__":
    limpar_diretorio("results/csv", extensoes=[".csv"])
    limpar_diretorio("results/figs", extensoes=[".png"])
    limpar_diretorio("results", extensoes=[".csv", ".png"])
    main()
    limpar_cache_py()
