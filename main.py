"""
Script principal para execução de experimentos de otimização do sistema elétrico.
Executa o modelo para diferentes valores de delta e configurações, armazena e exporta os resultados.

Autor: Giovani Santiago Junqueira
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
from power_opt.utils import DataLoader
from power_opt.solver import PyomoSolver


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
    resultados = []

    for i, delta in enumerate(deltas):
        print(f"🔁 Execução {i+1}/{len(deltas)} | delta = {delta}")

        # Carregar sistema
        system = DataLoader(json_path).load_system()
        system.config.update(config_base)
        system.config["delta"] = delta

        # Rodar modelo
        modelo = PyomoSolver(
            system,
            considerar_fluxo=config_base.get("considerar_fluxo", True),
            considerar_perdas=config_base.get("considerar_perdas", True),
            considerar_rampa=config_base.get("considerar_rampa", True),
            considerar_emissao=config_base.get("considerar_emissao", True)
        )
        modelo.modo_debug = True
        modelo.debug_csv_path = "results/debug_perdas.csv"
        modelo.construir()
        # modelo.model.pprint()
        solver_nome = config_base.get("solver_name", "highs").lower()
        modelo.solve(solver_name=solver_nome, tee=False)
        if solver_nome == "glpk":
            df_duais = modelo.get_duais()
            salvar_duais(df_duais, momento="experimentos", execucao=i, config_base=config_base)

        # Capturar resultados
        resultado = modelo.get_result()
        resultado["execucao"] = i
        resultados.append(resultado)

    return pd.DataFrame(resultados)

def simular_n_menos_1(json_path: str, config_base: dict) -> pd.DataFrame:
    """
    Executa simulações N-1, removendo um gerador ou uma linha por vez,
    e retorna um DataFrame com os resultados de cada cenário.

    Args:
        json_path (str): Caminho para o arquivo JSON com os dados do sistema.
        config_base (dict): Configurações padrão para cada execução.

    Returns:
        pd.DataFrame: Resultados de cada simulação N-1.
    """
    resultados = []

    # Carregar sistema base
    sistema_base = DataLoader(json_path).load_system()

    # N-1 para geradores
    geradores_base = [
        g for bus in sistema_base.buses.values()
        for g in bus.generators if not g.id.startswith("GF")
    ]
    for i, gerador in enumerate(geradores_base):
        print(f"🔁 N-1 Gerador {i+1}/{len(geradores_base)} | removendo: {gerador.id}")
        sistema = DataLoader(json_path).load_system()
        sistema.config.update(config_base)

        # Remove gerador
        sistema.get_bus(gerador.bus).generators = [
            g for g in sistema.get_bus(gerador.bus).generators if g.id != gerador.id
        ]
        bus = sistema.get_bus(gerador.bus)
        bus.generators = [g for g in bus.generators if g.id != gerador.id]

        modelo = PyomoSolver(
            sistema,
            considerar_fluxo=config_base.get("considerar_fluxo", False),
            considerar_perdas=config_base.get("considerar_perdas", False),
            considerar_rampa=config_base.get("considerar_rampa", False),
            considerar_emissao=config_base.get("considerar_emissao", False)
        )
        modelo.modo_debug = False
        modelo.construir()
        solver_nome = config_base.get("solver_name", "highs").lower()
        modelo.solve(solver_name=solver_nome, tee=False)
        if solver_nome == "glpk":
            df_duais = modelo.get_duais()
            salvar_duais(df_duais, momento="n_menos_1", cenario=f"sem_{gerador.id}",
                         config_base=config_base)
        resultado = modelo.get_result()
        resultado["cenario"] = f"sem_{gerador.id}"
        resultados.append(resultado)

    # N-1 para linhas
    for i, linha in enumerate(list(sistema_base.lines)):
        print(f"🔁 N-1 Linha {i+1}/{len(sistema_base.lines)} | removendo: {linha.id}")
        sistema = DataLoader(json_path).load_system()
        sistema.config.update(config_base)

        # Remove linha
        sistema.lines = [l for l in sistema.lines if l.id != linha.id]
        sistema.update_line_dict()

        modelo = PyomoSolver(
            sistema,
            considerar_fluxo=config_base.get("considerar_fluxo", False),
            considerar_perdas=config_base.get("considerar_perdas", False),
            considerar_rampa=config_base.get("considerar_rampa", False),
            considerar_emissao=config_base.get("considerar_emissao", False)
        )

        modelo.construir()
        modelo.solve(solver_name=solver_nome, tee=False)
        if solver_nome == "glpk":
            df_duais = modelo.get_duais()
            salvar_duais(df_duais, momento="n_menos_1", cenario=f"sem_{linha.id}",
                         config_base=config_base)
        resultado = modelo.get_result()
        resultado["cenario"] = f"sem_{linha.id}"
        resultados.append(resultado)

    return pd.DataFrame(resultados)

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

    # Salva o gráfico automaticamente
    plt.savefig("results/resultados_delta_vs_fob.png", dpi=300, bbox_inches="tight")

    plt.show()

def plot_delta_vs_fob_comparacao(
    df_sem_perda: pd.DataFrame,
    df_com_perda: pd.DataFrame,
    nome_arquivo: str = "results/comparacao_delta_vs_fob.png"
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

    # Plotagem dos dois conjuntos de dados
    plt.plot(df_sem_perda["delta"], df_sem_perda["FOB"],
             marker='o', markersize=4, linestyle='-', label="Sem Perda")

    plt.plot(df_com_perda["delta"], df_com_perda["FOB"],
             marker='s', markersize=4, linestyle='--', label="Com Perda")

    # Configurações do gráfico
    plt.title("Comparação da FOB com e sem Perda")
    plt.xlabel("Delta")
    plt.ylabel("FOB (Função Objetivo)")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()

    # Salvar o gráfico
    plt.savefig(nome_arquivo, dpi=300, bbox_inches="tight")
    plt.show()

def plot_n_menos_1_viabilidade(df_n_menos_1: pd.DataFrame):
    """
    Gera um gráfico de barras horizontais mostrando o FOB dos diferentes cenários N-1,
    com destaque para os cenários inviáveis (com geração fictícia).

    Args:
        df_n_menos_1 (pd.DataFrame): DataFrame com os resultados do N-1.
    """

    # Detecta inviabilidade pela presença de geração fictícia
    df_n_menos_1["viavel"] = (df_n_menos_1.get("ger_GF2_0", 0.0) == 0.0) & \
                             (df_n_menos_1.get("ger_GF2_1", 0.0) == 0.0) & \
                             (df_n_menos_1.get("ger_GF2_2", 0.0) == 0.0) & \
                             (df_n_menos_1.get("ger_GF3_0", 0.0) == 0.0) & \
                             (df_n_menos_1.get("ger_GF3_1", 0.0) == 0.0) & \
                             (df_n_menos_1.get("ger_GF3_2", 0.0) == 0.0)

    # Ordena por FOB
    df_sorted = df_n_menos_1.sort_values("FOB", ascending=False)

    # Cores com base na viabilidade
    cores = ["tab:green" if v else "tab:red" for v in df_sorted["viavel"]]

    plt.figure(figsize=(10, 12))
    plt.barh(df_sorted["cenario"], df_sorted["FOB"], color=cores)
    plt.title("FOB por Cenário N-1 (Verde = Viável, Vermelho = Inviável)")
    plt.xlabel("FOB")
    plt.ylabel("Cenário")
    plt.tight_layout()

    # Salva o gráfico automaticamente
    plt.savefig("results/resultados_n_menos_1.png", dpi=300, bbox_inches="tight")

    plt.show()

def salvar_duais(df_duais: pd.DataFrame, momento: str,
                 execucao: int | None = None, cenario: str | None = None,
                 config_base: dict | None = None):
    """
    Salva variáveis duais significativamente diferentes de zero em um único CSV,
    com metadados claros sobre o momento da simulação e configuração utilizada.

    Args:
        df_duais (pd.DataFrame): DataFrame contendo os multiplicadores de Lagrange.
        momento (str): Identificador do estágio da simulação ("experimentos", "n_menos_1" etc.).
        execucao (int, optional): Índice da execução, se aplicável.
        cenario (str, optional): Identificador do cenário, se aplicável.
        config_base (dict, optional): Dicionário com as flags de configuração usadas.
    """
    # Filtra apenas as duais ativas (diferentes de zero)
    df_filtrado = df_duais[df_duais["dual"] != 0.0].copy()
    if df_filtrado.empty:
        return  # Nada a salvar

    # Adiciona informações de contexto
    df_filtrado["momento"] = momento
    if execucao is not None:
        df_filtrado["execucao"] = execucao
    if cenario is not None:
        df_filtrado["cenario"] = cenario

    # Adiciona descrição legível das configurações
    if config_base:
        config_str = "_".join([
            f"fluxo={config_base.get('considerar_fluxo', False)}",
            f"perdas={config_base.get('considerar_perdas', False)}",
            f"emissao={config_base.get('considerar_emissao', False)}",
            f"rampa={config_base.get('considerar_rampa', False)}"
        ])
        df_filtrado["config_str"] = config_str
    else:
        df_filtrado["config_str"] = "indefinido"

    # Salva no CSV
    path = "results/duais_acumulado.csv"
    header = not os.path.exists(path)
    df_filtrado.to_csv(path, mode="a", header=header, index=False)

def main():
    """
    Função principal para configurar e executar os experimentos de otimização.
    Salva os resultados em um arquivo CSV.
    """
    json_path = "data/dados_base.json"
    deltas = [round(0.01 * i, 2) for i in range(0, 101)]
    # deltas = [1]
    config_base = {
        "solver_name": "glpk",
        # "solver_name": "highs",
        "considerar_fluxo": True,
        "considerar_perdas": True,
        "considerar_rampa": True,
        "considerar_emissao": True
    }

    df_resultados = executar_experimentos(json_path, deltas, config_base)
    df_resultados.to_csv("results/resultados_otimizacao.csv", index=False)
    print("✅ Experimentos concluídos e resultados salvos em 'resultados_otimizacao.csv'")

    # Experimentos N-1
    df_n_menos_1 = simular_n_menos_1(json_path, config_base)
    df_n_menos_1.to_csv("results/resultados_n_menos_1.csv", index=False)
    print("✅ Resultados N-1 salvos em 'resultados_n_menos_1.csv'")


    deltas = [round(0.01 * i, 2) for i in range(0, 101)]
    # deltas = [1]
    config_base = {
        "solver_name": "glpk",
        # "solver_name": "highs",
        "considerar_fluxo": True,
        "considerar_perdas": False,
        "considerar_rampa": True,
        "considerar_emissao": True
    }
    # sem perdas
    df_sem_perdas = executar_experimentos(json_path, deltas, config_base)
    df_sem_perdas.to_csv("results/resultados_sem_perdas.csv", index=False)
    print("✅ Experimentos concluídos e resultados salvos em 'resultados_perdas.csv'")

    plot_delta_vs_fob(df_resultados)
    plot_delta_vs_fob_comparacao(df_sem_perdas, df_resultados)
    plot_n_menos_1_viabilidade(df_n_menos_1)

if __name__ == "__main__":
    main()
