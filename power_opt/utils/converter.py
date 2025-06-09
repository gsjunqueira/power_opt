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

def preparar_n_menos_1(df: pd.DataFrame) -> pd.DataFrame:
    """
    Converte o DataFrame de resultados N-1 do formato long para wide,
    criando colunas como 'ger_GF2_0', 'deficit_B2_1', etc. e incluindo FOB.

    Args:
        df (pd.DataFrame): DataFrame com resultados no formato long.

    Returns:
        pd.DataFrame: DataFrame formatado no estilo wide para análise.
    """
    # Separar FOB
    df_fob = df[df["tipo"] == "FOB"][["simulacao", "valor"]].rename(columns={"valor": "FOB"})

    # Filtrar os tipos que queremos pivotar
    df_variaveis = df[df["tipo"] != "FOB"].copy()
    df_variaveis["coluna"] = df_variaveis["tipo"] + "_" + df_variaveis["id"].astype(str)
    df_variaveis.loc[df_variaveis["tempo"].notna(), "coluna"] += "_" + df_variaveis["tempo"].astype(int).astype(str)

    # Pivotar
    df_wide = df_variaveis.pivot_table(index="simulacao", columns="coluna", values="valor", aggfunc="first")

    # Juntar com FOB
    df_final = df_wide.reset_index().merge(df_fob, on="simulacao", how="left")

    # Extrair cenário removido do sufixo do identificador
    df_final["cenario"] = df_final["simulacao"].str.extract(r'_(.*)$')[0]

    # Identificar viabilidade: qualquer déficit > 0 ou gerador fictício > 0 → inviável
    colunas_deficit = [c for c in df_final.columns if c.startswith("deficit_")]
    colunas_ger_fict = [c for c in df_final.columns if c.startswith("geracao_GF")]

    # Define condição de inviabilidade
    cond_deficit = df_final[colunas_deficit].fillna(
        0).gt(1e-6).any(axis=1) if colunas_deficit else pd.Series([False]*len(df_final))
    cond_ger_fict = df_final[colunas_ger_fict].fillna(
        0).gt(1e-6).any(axis=1) if colunas_ger_fict else pd.Series([False]*len(df_final))

    df_final["viavel"] = ~(cond_deficit | cond_ger_fict)

    return df_final
