"""
Script principal para execução de experimentos de otimização do sistema elétrico.
Executa o modelo para diferentes valores de delta e configurações, armazena e exporta os resultados.

Autor: Giovani Santiago Junqueira
"""

import time
import pandas as pd
from power_opt.utils import (
    DataLoader, limpar_cache_py, limpar_diretorio,
    preparar_df, preparar_dados_graficos
)
from power_opt.solver import PyomoSolver
from power_opt.solver.handler import (
    extrair_resultados,
    salvar_resultados_em_csv,
    extrair_duais_em_dataframe,
    plot_all,
    plot_delta_vs_fob,
    plot_delta_vs_fob_comparacao,
    # # plot_n_menos_1_viabilidade
)

def split_config(config):
    """
    Separa um dicionário de configuração em dois subconjuntos:
    um para a construção do modelo (Pyomo) e outro para a resolução (solver).

    Essa função permite que todas as configurações do experimento sejam passadas
    por um único dicionário, mantendo a modularidade e evitando alterações internas
    nos métodos `build()` e `solve()`.

    Args:
        config (dict): Dicionário de entrada contendo todas as configurações do experimento,
            incluindo chaves como 'solver_name', 'tee', 'considerar_fluxo', entre outras.

    Returns:
        tuple:
            config_modelo (dict): Subconjunto do dicionário contendo apenas os parâmetros
                relevantes para a construção do modelo (e.g., considerar_fluxo, considerar_emissao).
            config_solver (dict): Subconjunto do dicionário contendo os parâmetros relevantes
                para o solver (e.g., solver_name, tee, tolerancia).

    Example:
        config = {
            "solver_name": "highs",
            "tee": False,
            "considerar_emissao": True,
            "considerar_fluxo": True
        }

        config_modelo, config_solver = split_config(config)
    """
    solver_keys = {"solver_name", "tee", "tolerancia"}
    config_solver = {k: v for k, v in config.items() if k in solver_keys}
    config_modelo = {k: v for k, v in config.items() if k not in solver_keys}
    return config_modelo, config_solver

def executar_experimentos(json_path: str, deltas: list[float], config_base: dict) -> pd.DataFrame:
    """
    Executa a otimização do sistema elétrico para diferentes valores de delta.

    Args:
        json_path (str): Caminho para o arquivo JSON com os dados do sistema.
        deltas (list[float]): Lista de valores de delta a serem testados.
        config_base (dict): Dicionário com as configurações padrão para cada execução.

    Returns:
        pd.DataFrame: DataFrame contendo os resultados de todas as execuções.
    """
    inicio = time.time()
    resultados = []

    for i, delta in enumerate(deltas):
        print(f"🔁 Execução {i+1}/{len(deltas)} | delta = {delta}")

        # Carregar sistema
        system = DataLoader(json_path, {"usar_deficit": config_base.get(
            "usar_deficit", False)}).load_system()

        system.config.update(config_base)
        system.config["delta"] = delta

        # Criar solver
        modelo = PyomoSolver(system)
        config_modelo, config_solver = split_config(config_base)
        solver_nome = config_solver.get("solver_name", "highs").lower()
        modelo.build(**config_modelo)
        modelo.solve(**config_solver)

        # Capturar duais se GLPK
        if solver_nome == "glpk":
            df_duais = extrair_duais_em_dataframe(modelo.model)
            df_duais["caso"] = i
            df_duais.to_csv("results/csv/duais.csv", mode="a", header=not bool(i), index=False)

        # Capturar resultados
        resultado = extrair_resultados(modelo, system=system)
        resultado["execucao"] = i
        resultados.append(resultado)

    fim = time.time()
    return resultados, (fim - inicio) / len(deltas)

def main():
    """
    Função principal para configurar e executar os experimentos de otimização.
    Salva os resultados em arquivos CSV e gera gráficos.
    """
    inicio_total = time.time()
    json_path = "data/dados_base.json"
    deltas = [round(0.01 * i, 2) for i in range(0, 101)]
    # deltas = [round(0.1 * i, 2) for i in range(0, 11)]
    # deltas = [1]
    config_base_com_perda = {
        "solver_name": "glpk", # "highs",
        "usar_deficit": True,
        "considerar_fluxo": True,
        "considerar_perdas": True,
        "considerar_rampa": True,
        "considerar_emissao": True
    }

    config_base_sem_perda = config_base_com_perda.copy()
    config_base_sem_perda["considerar_perdas"] = False
    simulacoes = []
    df_com_perda, tempo_com_perda = executar_experimentos(json_path, deltas, config_base_com_perda)
    simulacoes.append(df_com_perda)
    df_sem_perda, tempo_sem_perda = executar_experimentos(json_path, deltas, config_base_sem_perda)
    simulacoes.append(df_sem_perda)
    salvar_resultados_em_csv(simulacoes, "results/csv/simulacoes.csv")
    salvar_resultados_em_csv(df_com_perda, "results/csv/resultados_com_perda.csv")
    salvar_resultados_em_csv(df_sem_perda, "results/csv/resultados_sem_perda.csv")
    print("✅ Resultados salvos em 'results/csv/'")

    df_geracao, df_fluxo, df_deficit, df_perda = preparar_dados_graficos(df_com_perda)
    fob_com_perda = preparar_df(pd.concat(df_com_perda, ignore_index=True))
    fob_sem_perda = preparar_df(pd.concat(df_sem_perda, ignore_index=True))

    fim_total = time.time()

    plot_all(df_geracao, df_fluxo, df_deficit, df_perda, 'results/figs')


    # Geração de gráficos
    plot_delta_vs_fob(fob_com_perda, com_perda=True, nome_arquivo="results/figs/fob_com_perda.png")
    plot_delta_vs_fob(fob_sem_perda, com_perda=False, nome_arquivo="results/figs/fob_sem_perda.png")
    plot_delta_vs_fob_comparacao(fob_sem_perda, fob_com_perda)

    print(
        f"⏱️ Tempo total das {2 * len(deltas)} simulações: {(fim_total - inicio_total):.2f} segundos")
    print(
        f"⏱️ Tempo médio com perdas: {tempo_com_perda:.2f} s | sem perdas: {tempo_sem_perda:.2f} s")


if __name__ == "__main__":
    limpar_diretorio("results/csv", extensoes=[".csv"])
    limpar_diretorio("results/figs", extensoes=[".png"])
    limpar_diretorio("results", extensoes=[".csv", ".png"])
    main()
    # limpar_cache_py()
