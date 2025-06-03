"""
Módulo `converter`

Este módulo contém funções utilitárias para transformar os resultados brutos da otimização
em DataFrames organizados e estruturados. Os dados resultantes são compatíveis com a geração
de gráficos e relatórios consolidados, facilitando a análise dos experimentos simulados.

Autor: Giovani Santiago Junqueira
"""

__author__ = "Giovani Santiago Junqueira"

import pandas as pd

def preparar_dados_graficos(lista_resultados: list) -> tuple[pd.DataFrame, pd.DataFrame,
                                                             pd.DataFrame, pd.DataFrame]:
    """
    Converte os resultados consolidados da simulação em DataFrames formatados para os gráficos:
    geração, fluxo, perda e déficit.

    Args:
        lista_resultados (list[dict]): Lista de dicionários contendo resultados das simulações.

    Returns:
        Tuple contendo:
        - df_geracao: DataFrame com colunas ['gerador', 'tempo', 'valor']
        - df_fluxo: DataFrame com colunas ['linha', 'tempo', 'valor']
        - df_perda: DataFrame com colunas ['linha', 'tempo', 'valor']
        - df_deficit: DataFrame com colunas ['barra', 'tempo', 'valor']
    """
    dados_geracao = []
    dados_fluxo = []
    dados_perda = []
    dados_deficit = []

    for resultado in lista_resultados:
        for entrada in resultado.get("dados", []):
            tipo = entrada["tipo"]
            id_ = entrada["id"]
            tempo = entrada["tempo"]
            valor = entrada["valor"]

            if tipo == "geracao":
                dados_geracao.append({"gerador": id_, "tempo": tempo, "valor": valor})
            elif tipo == "fluxo":
                dados_fluxo.append({"linha": id_, "tempo": tempo, "valor": valor})
            elif tipo == "perda":
                dados_perda.append({"linha": id_, "tempo": tempo, "valor": valor})
            elif tipo == "deficit":
                dados_deficit.append({"barra": id_, "tempo": tempo, "valor": valor})

    df_geracao = pd.DataFrame(dados_geracao)
    df_fluxo = pd.DataFrame(dados_fluxo)
    df_perda = pd.DataFrame(dados_perda)
    df_deficit = pd.DataFrame(dados_deficit)

    return df_geracao, df_fluxo, df_perda, df_deficit

def preparar_df_plot_comparacoes(df_resultados: pd.DataFrame
                                 ) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Prepara os DataFrames necessários para os gráficos de comparação de FOB com e sem perda
    e para análise de variação com Delta.

    Args:
        df_resultados (pd.DataFrame): DataFrame consolidado contendo colunas como
            ['delta', 'FOB', 'Perdas', ...].

    Returns:
        tuple:
            - df_delta_fob (pd.DataFrame): Dados agrupados por Delta e média do FOB.
            - df_sem_perda (pd.DataFrame): Simulações sem consideração de perdas.
            - df_com_perda (pd.DataFrame): Simulações com consideração de perdas.
    """
    if "delta" not in df_resultados.columns or "FOB" not in df_resultados.columns:
        raise ValueError("O DataFrame deve conter as colunas 'delta' e 'FOB'.")

    # Subconjuntos por condição
    df_sem_perda = df_resultados[df_resultados["Perdas"].is_(False)].copy()
    df_com_perda = df_resultados[df_resultados["Perdas"].is_(True)].copy()

    # Média FOB por delta (caso haja mais de uma simulação por delta)
    df_delta_fob = df_resultados.groupby("delta", as_index=False)["FOB"].mean()

    return df_delta_fob, df_sem_perda, df_com_perda
