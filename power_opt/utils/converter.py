"""
Módulo `converter`

Este módulo contém funções utilitárias para transformar os resultados brutos da otimização
em DataFrames organizados e estruturados. Os dados resultantes são compatíveis com a geração
de gráficos e relatórios consolidados, facilitando a análise dos experimentos simulados.

Autor: Giovani Santiago Junqueira
"""

__author__ = "Giovani Santiago Junqueira"

import pandas as pd

def preparar_dados_graficos(lista_resultados: list[pd.DataFrame]) -> tuple[pd.DataFrame, pd.DataFrame,
                                                                            pd.DataFrame, pd.DataFrame]:
    """
    Converte os resultados consolidados da simulação em DataFrames formatados para os gráficos:
    geração, fluxo, perda e déficit.

    Args:
        lista_resultados (list[pd.DataFrame]): Lista de DataFrames contendo resultados das simulações.

    Returns:
        Tuple contendo:
        - df_geracao: DataFrame com colunas ['id', 'tempo', 'valor', 'execucao']
        - df_fluxo: DataFrame com colunas ['id', 'tempo', 'valor', 'execucao']
        - df_perda: DataFrame com colunas ['id', 'tempo', 'valor', 'execucao']
        - df_deficit: DataFrame com colunas ['id', 'tempo', 'valor', 'execucao']
    """
    df_total = pd.concat(lista_resultados, ignore_index=True)

    df_geracao = df_total[df_total["tipo"] == "geracao"]
    df_fluxo = df_total[df_total["tipo"] == "fluxo"]
    df_perda = df_total[df_total["tipo"] == "perda"]
    df_deficit = df_total[df_total["tipo"] == "deficit"]

    return df_geracao, df_fluxo, df_perda, df_deficit

def preparar_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Extrai pares (delta, FOB) de um DataFrame de resultados baseado no campo 'simulacao'
    e no filtro 'tipo' == 'FOB'.

    Args:
        df (pd.DataFrame): DataFrame com colunas ['simulacao', 'tipo', 'valor']

    Returns:
        pd.DataFrame: DataFrame com colunas ['delta', 'FOB']
    """
    # Filtra somente linhas com tipo FOB
    df_fob = df[df["tipo"] == "FOB"].copy()

    # Extrai delta da string simulacao (parte numérica no início)
    df_fob["delta"] = df_fob["simulacao"].str.extract(r"^(\d{1,3})").astype(int)

    # Renomeia a coluna 'valor' para 'FOB' e seleciona apenas as colunas relevantes
    df_fob = df_fob.rename(columns={"valor": "FOB"})[["delta", "FOB"]]

    return df_fob
