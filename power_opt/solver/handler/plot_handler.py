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


def plot_delta_vs_fob(df_otimizacao: pd.DataFrame):
    """
    Gera um gráfico de linha mostrando a relação entre o valor de delta e o FOB (função objetivo).

    Args:
        df_otimizacao (pd.DataFrame): DataFrame contendo os resultados dos experimentos com
        diferentes deltas.
    """
    plt.figure(figsize=(10, 5))
    plt.plot(df_otimizacao["delta"], df_otimizacao["FOB"], marker='o', markersize=2, linestyle='-')
    plt.title("Variação do FOB com o Delta")
    plt.xlabel("Delta")
    plt.ylabel("FOB (Função Objetivo)")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("results/figs/resultados_delta_vs_fob.png", dpi=300, bbox_inches="tight")
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
    df_n_menos_1["viavel"] = (df_n_menos_1.get("ger_GF2_0", 0.0) == 0.0) & \
                             (df_n_menos_1.get("ger_GF2_1", 0.0) == 0.0) & \
                             (df_n_menos_1.get("ger_GF2_2", 0.0) == 0.0) & \
                             (df_n_menos_1.get("ger_GF3_0", 0.0) == 0.0) & \
                             (df_n_menos_1.get("ger_GF3_1", 0.0) == 0.0) & \
                             (df_n_menos_1.get("ger_GF3_2", 0.0) == 0.0)

    df_sorted = df_n_menos_1.sort_values("FOB", ascending=False)
    cores = ["tab:green" if v else "tab:red" for v in df_sorted["viavel"]]
    plt.figure(figsize=(10, 12))
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
    for g in df_geracao["gerador"].unique():
        dados = df_geracao[df_geracao["gerador"] == g]
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
    for l in df_fluxo["linha"].unique():
        dados = df_fluxo[df_fluxo["linha"] == l]
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
    for l in df_perda["linha"].unique():
        dados = df_perda[df_perda["linha"] == l]
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
    for b in df_deficit["barra"].unique():
        dados = df_deficit[df_deficit["barra"] == b]
        plt.plot(dados["tempo"], dados["valor"], marker='x', label=b)

    plt.title("Déficit por Barra ao Longo do Tempo")
    plt.xlabel("Tempo")
    plt.ylabel("Déficit (MW)")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
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

    if df_fluxo is not None:
        plot_fluxo(df_fluxo, output_path=os.path.join(pasta_saida, "grafico_fluxo.png"))

    if df_perda is not None:
        plot_perda(df_perda, output_path=os.path.join(pasta_saida, "grafico_perda.png"))

    if df_deficit is not None:
        plot_deficit(df_deficit, output_path=os.path.join(pasta_saida, "grafico_deficit.png"))
