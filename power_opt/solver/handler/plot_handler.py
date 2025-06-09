"""
Módulo `plot_handler`

Responsável pela geração de gráficos para análise de resultados da otimização.
Inclui visualizações como:
- FOB vs Delta
- Comparação de FOB com/sem perdas
- Viabilidade dos cenários N-1
- Geração por gerador ao longo do tempo
- Fluxo por linha ao longo do tempo
- Perda por linha ao longo do tempo
- Déficit por barra ao longo do tempo

Autor: Giovani Santiago Junqueira
"""

__author__ = "Giovani Santiago Junqueira"

# pylint: disable=line-too-long

import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


def plot_delta_vs_fob(df_otimizacao: pd.DataFrame, com_perda: bool, nome_arquivo: str):
    """
    Gera um gráfico de linha mostrando a relação entre o valor de delta e o FOB (função objetivo).

    Args:
        df_otimizacao (pd.DataFrame): DataFrame contendo os resultados dos experimentos com
        diferentes deltas.
    """
    titulo = "Variação do FOB com o Delta (Com Perda)" if com_perda else "Variação do FOB com o Delta (Sem Perda)"
    plt.figure(figsize=(10, 5))
    plt.plot(df_otimizacao["delta"], df_otimizacao["FOB"], marker='o', markersize=2, linestyle='-')
    plt.title(titulo)
    plt.xlabel("Delta")
    plt.ylabel("FOB (Função Objetivo)")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(nome_arquivo, dpi=300, bbox_inches="tight")
    plt.show()


def plot_delta_vs_fob_comparacao(
    df_sem_perda: pd.DataFrame,
    df_com_perda: pd.DataFrame,
    nome_arquivo: str = "results/figs/comparacao_delta_vs_fob.png"
):
    """
    Gera um gráfico comparando a variação do FOB em função do Delta
    para duas condições: sem perda e com perda.

    Args:
        df_sem_perda (pd.DataFrame): DataFrame com resultados SEM consideração de perdas.
        df_com_perda (pd.DataFrame): DataFrame com resultados COM consideração de perdas.
        nome_arquivo (str): Nome do arquivo de imagem para salvar o gráfico.
    """
    plt.figure(figsize=(10, 5))
    plt.plot(df_sem_perda["delta"], df_sem_perda["FOB"],
             marker='o', markersize=4, linestyle='-', label="Sem Perda")
    plt.plot(df_com_perda["delta"], df_com_perda["FOB"],
             marker='s', markersize=4, linestyle='--', label="Com Perda")
    plt.title("Comparação da FOB com e sem Perda")
    plt.xlabel("Delta")
    plt.ylabel("FOB (Função Objetivo)")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(nome_arquivo, dpi=300, bbox_inches="tight")
    plt.show()


def plot_n_menos_1_viabilidade(df_n_menos_1: pd.DataFrame):
    """
    Gera um gráfico de barras horizontais mostrando o FOB dos diferentes cenários N-1,
    com destaque para os cenários inviáveis (com geração fictícia).

    Args:
        df_n_menos_1 (pd.DataFrame): DataFrame com os resultados do N-1.
    """

    df_sorted = df_n_menos_1.sort_values("FOB", ascending=False)
    cores = ["tab:green" if v else "tab:red" for v in df_sorted["viavel"]]
    plt.figure(figsize=(6, 6))
    plt.barh(df_sorted["cenario"], df_sorted["FOB"], color=cores)
    plt.title("FOB por Cenário N-1 (Verde = Viável, Vermelho = Inviável)")
    plt.xlabel("FOB")
    plt.ylabel("Cenário")
    plt.tight_layout()
    plt.savefig("results/figs/resultados_n_menos_1.png", dpi=300, bbox_inches="tight")
    plt.show()

def plot_geracao(df_geracao: pd.DataFrame, output_path: str = "results/figs/grafico_geracao.png"):
    """
    Gera um gráfico de linha da geração por gerador ao longo do tempo.

    Args:
        df_geracao (pd.DataFrame): DataFrame contendo colunas ['gerador', 'tempo', 'valor'].
        output_path (str): Caminho do arquivo de imagem a ser salvo.
    """
    plt.figure(figsize=(10, 6))
    for g in df_geracao["id"].unique():
        dados = df_geracao[df_geracao["id"] == g]
        plt.plot(dados["tempo"], dados["valor"], marker='o', label=g)

    plt.title("Geração por Gerador ao Longo do Tempo")
    plt.xlabel("Tempo")
    plt.ylabel("Geração (MW)")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()


def plot_fluxo(df_fluxo: pd.DataFrame, output_path: str = "results/figs/grafico_fluxo.png"):
    """
    Gera um gráfico de linha com os fluxos de cada linha ao longo do tempo.

    Args:
        df_fluxo (pd.DataFrame): DataFrame contendo colunas ['linha', 'tempo', 'valor'].
        output_path (str): Caminho do arquivo de imagem a ser salvo.
    """
    plt.figure(figsize=(10, 6))
    for l in df_fluxo["id"].unique():
        dados = df_fluxo[df_fluxo["id"] == l]
        plt.plot(dados["tempo"], dados["valor"], marker='s', label=l)

    plt.title("Fluxo por Linha ao Longo do Tempo")
    plt.xlabel("Tempo")
    plt.ylabel("Fluxo (pu)")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()


def plot_perda(df_perda: pd.DataFrame, output_path: str = "results/figs/grafico_perda.png"):
    """
    Gera um gráfico de linha com as perdas por linha ao longo do tempo.

    Args:
        df_perda (pd.DataFrame): DataFrame contendo colunas ['linha', 'tempo', 'valor'].
        output_path (str): Caminho do arquivo de imagem a ser salvo.
    """
    plt.figure(figsize=(10, 6))
    for l in df_perda["id"].unique():
        dados = df_perda[df_perda["id"] == l]
        plt.plot(dados["tempo"], dados["valor"], marker='^', label=l)

    plt.title("Perda por Linha ao Longo do Tempo")
    plt.xlabel("Tempo")
    plt.ylabel("Perda (MW)")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()


def plot_deficit(df_deficit: pd.DataFrame, output_path: str = "results/figs/grafico_deficit.png"):
    """
    Gera um gráfico de linha com os déficits por barra ao longo do tempo.

    Args:
        df_deficit (pd.DataFrame): DataFrame contendo colunas ['barra', 'tempo', 'valor'].
        output_path (str): Caminho do arquivo de imagem a ser salvo.
    """
    plt.figure(figsize=(10, 6))
    for b in df_deficit["id"].unique():
        dados = df_deficit[df_deficit["id"] == b]
        plt.plot(dados["tempo"], dados["valor"], marker='x', label=b)

    plt.title("Déficit por Barra ao Longo do Tempo")
    plt.xlabel("Tempo")
    plt.ylabel("Déficit (MW)")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()

def plot_box_geracao(df_geracao, output_path: str = "results/figs/boxplot_geracao.png"):
    """
    Gera um boxplot da geração por gerador e tempo.

    Cada gerador-tempo (ex: GT1_t0, GT2_t1) é representado como uma categoria
    distinta no eixo X, permitindo observar a variação da geração em diferentes
    simulações.

    Parâmetros:
    ------------
    df_geracao : pd.DataFrame
        DataFrame contendo colunas ['id', 'tempo', 'valor'] e múltiplas execuções.

    output_path : str
        Caminho para salvar a figura PNG gerada.
    """
    df_geracao["id_tempo"] = df_geracao["id"] + "_t" + df_geracao["tempo"].astype(str)

    plt.figure(figsize=(6, 6))
    sns.boxplot(x="id_tempo", y="valor", data=df_geracao, width=0.4)
    plt.title("Boxplot de Geração por Gerador e Tempo")
    plt.xlabel("Gerador_Tempo")
    plt.ylabel("Geração (MW)")
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()

def plot_box_fluxo(df_fluxo, output_path: str = "results/figs/boxplot_fluxo_por_idtempo.png"):
    """
    Gera um boxplot do fluxo de potência por linha e tempo.

    Cada linha-tempo (ex: L0_t0, L3_t2) representa um ponto de observação
    independente para analisar a variação de fluxos ao longo das execuções.

    Parâmetros:
    ------------
    df_fluxo : pd.DataFrame
        DataFrame com colunas ['id', 'tempo', 'valor'].

    output_path : str
        Caminho para salvar o gráfico em formato PNG.
    """
    df_fluxo["id_tempo"] = df_fluxo["id"] + "_t" + df_fluxo["tempo"].astype(str)

    plt.figure(figsize=(6, 6))
    sns.boxplot(x="id_tempo", y="valor", data=df_fluxo, width=0.4)
    plt.title("Boxplot de Fluxo por Linha e Tempo")
    plt.xlabel("Linha_Tempo")
    plt.ylabel("Fluxo (pu)")
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()

def plot_box_deficit(df_deficit, output_path: str = "results/figs/boxplot_deficit_por_idtempo.png"):
    """
    Gera um boxplot do déficit por barra e tempo ao longo das simulações.

    Permite visualizar a distribuição do corte de carga em diferentes barras
    para cada instante de tempo modelado.

    Parâmetros:
    ------------
    df_deficit : pd.DataFrame
        DataFrame com colunas ['id', 'tempo', 'valor'].

    output_path : str
        Caminho de saída do gráfico PNG.
    """
    df_deficit["id_tempo"] = df_deficit["id"] + "_t" + df_deficit["tempo"].astype(str)

    plt.figure(figsize=(6, 6))
    sns.boxplot(x="id_tempo", y="valor", data=df_deficit, width=0.4)
    plt.title("Boxplot de Déficit por Barra e Tempo")
    plt.xlabel("Barra_Tempo")
    plt.ylabel("Déficit (MW)")
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()

def plot_box_perda(df_perda, output_path: str = "results/figs/boxplot_perda_por_idtempo.png"):
    """
    Gera um boxplot da perda por linha e tempo em todas as simulações.

    O gráfico mostra a variação da perda estimada por linha em cada tempo,
    útil para identificar linhas críticas ou sobrecarregadas.

    Parâmetros:
    ------------
    df_perda : pd.DataFrame
        DataFrame com colunas ['id', 'tempo', 'valor'].

    output_path : str
        Caminho para salvar o arquivo PNG gerado.
    """
    df_perda["id_tempo"] = df_perda["id"] + "_t" + df_perda["tempo"].astype(str)

    plt.figure(figsize=(6, 6))
    sns.boxplot(x="id_tempo", y="valor", data=df_perda, width=0.4)
    plt.title("Boxplot de Perda por Linha e Tempo")
    plt.xlabel("Linha_Tempo")
    plt.ylabel("Perda (MW)")
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()

def plot_all(
    df_geracao: pd.DataFrame = None,
    df_fluxo: pd.DataFrame = None,
    df_perda: pd.DataFrame = None,
    df_deficit: pd.DataFrame = None,
    pasta_saida: str = "results"
):
    """
    Gera todos os gráficos disponíveis com base nos DataFrames fornecidos.

    Args:
        df_geracao (pd.DataFrame, opcional): DataFrame de geração com colunas ['gerador', 'tempo', 'valor'].
        df_fluxo (pd.DataFrame, opcional): DataFrame de fluxo com colunas ['linha', 'tempo', 'valor'].
        df_perda (pd.DataFrame, opcional): DataFrame de perdas com colunas ['linha', 'tempo', 'valor'].
        df_deficit (pd.DataFrame, opcional): DataFrame de déficit com colunas ['barra', 'tempo', 'valor'].
        pasta_saida (str): Caminho da pasta onde os gráficos serão salvos.
    """
    os.makedirs(pasta_saida, exist_ok=True)

    if df_geracao is not None:
        plot_geracao(df_geracao, output_path=os.path.join(pasta_saida, "grafico_geracao.png"))
        plot_box_geracao(df_geracao, output_path=os.path.join(pasta_saida, "boxplot_geracao.png"))

    if df_fluxo is not None:
        plot_fluxo(df_fluxo, output_path=os.path.join(pasta_saida, "grafico_fluxo.png"))
        plot_box_fluxo(df_fluxo, output_path=os.path.join(pasta_saida, "boxplot_fluxo.png"))

    if df_perda is not None:
        plot_perda(df_perda, output_path=os.path.join(pasta_saida, "grafico_perda.png"))
        plot_box_perda(df_perda, output_path=os.path.join(pasta_saida, "boxplot_perda.png"))

    if df_deficit is not None:
        plot_deficit(df_deficit, output_path=os.path.join(pasta_saida, "grafico_deficit.png"))
        plot_box_deficit(df_deficit, output_path=os.path.join(pasta_saida, "boxplot_deficit.png"))
