"""
Módulo `experimentos`

Este módulo executa uma série de simulações de despacho de geração elétrica utilizando o modelo de
otimização implementado em Pyomo. Cada simulação é realizada para um valor diferente do parâmetro
delta, que pondera o peso entre o custo de geração e a penalização por emissões.

Funcionalidades principais:
- Carregamento do sistema elétrico a partir de um arquivo JSON.
- Configuração dinâmica do parâmetro `delta` e das flags operacionais do modelo (ex: uso de déficit).
- Construção e resolução do modelo Pyomo para cada configuração.
- Extração dos resultados de geração, fluxo, perdas, déficit e custo total (FOB).
- Armazenamento opcional das variáveis duais caso o solver GLPK seja utilizado.

Este módulo é útil para análises comparativas de desempenho, sensibilidade e trade-offs
em sistemas de geração, especialmente quando múltiplas execuções são necessárias em lote.

Autor: Giovani Santiago Junqueira
"""

__author__ = "Giovani Santiago Junqueira"

import time
import pandas as pd
from power_opt.utils import DataLoader,  split_config
from power_opt.solver import PyomoSolver
from power_opt.solver.handler import extrair_resultados, extrair_duais_em_dataframe


def simular_delta(json_path: str, deltas: list[float], config_base: dict) -> pd.DataFrame:
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
        # print(f"🔁 Execução {i+1}/{len(deltas)} | delta = {delta}")

        # Carregar sistema
        system = DataLoader(json_path, {"deficit": config_base.get(
            "deficit", False)}).load_system()

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

def simular_n_menos_1(json_path: str, config_base: dict) -> pd.DataFrame:
    """
    Executa simulações N-1, removendo um gerador ou uma linha por vez.

    Args:
        json_path (str): Caminho para o arquivo JSON com os dados do sistema.
        config_base (dict): Configurações padrão para cada execução.

    Returns:
        pd.DataFrame: Resultados consolidados das simulações N-1.
    """
    resultados = []

    # Carregar sistema base
    sistema_base = DataLoader(
        json_path, {"deficit": config_base.get("deficit", False)}
    ).load_system()

    # Separar configurações
    config_modelo, config_solver = split_config(config_base)
    solver_nome = config_solver.get("solver_name", "highs").lower()

    # N-1 para geradores
    geradores_base = [
        g for bus in sistema_base.buses.values()
        for g in bus.generators if not g.id.startswith("GF")
    ]
    for i, gerador in enumerate(geradores_base):
        # print(f"🔁 N-1 Gerador {i+1}/{len(geradores_base)} | removendo: {gerador.id}")
        sistema = DataLoader(json_path,
                             {"deficit": config_base.get("deficit", False)}).load_system()
        sistema.config.update(config_base)

        # Remover o gerador
        bus = sistema.get_bus(gerador.bus)
        bus.generators = [g for g in bus.generators if g.id != gerador.id]

        # Criar e resolver modelo
        modelo = PyomoSolver(sistema)
        modelo.build(**config_modelo)
        modelo.solve(**config_solver)

        # Capturar duais se GLPK
        if solver_nome == "glpk":
            df_duais = extrair_duais_em_dataframe(modelo.model)
            df_duais["caso"] = i
            df_duais.to_csv("results/csv/duais.csv", mode="a", header=not bool(i), index=False)

        # Extrair resultados
        resultado = extrair_resultados(modelo, system=sistema, elemento_removido=gerador.id)
        resultados.append(resultado)

    # N-1 para linhas
    for i, linha in enumerate(sistema_base.lines):
        # print(f"🔁 N-1 Linha {i+1}/{len(sistema_base.lines)} | removendo: {linha.id}")
        sistema = DataLoader(json_path,
                             {"deficit": config_base.get("deficit", False)}).load_system()
        sistema.config.update(config_base)

        # Remover linha
        sistema.lines = [l for l in sistema.lines if l.id != linha.id]
        sistema.update_line_dict()

        # Criar e resolver modelo
        modelo = PyomoSolver(sistema)
        modelo.build(**config_modelo)
        modelo.solve(**config_solver)

        # Capturar duais se GLPK
        if solver_nome == "glpk":
            df_duais = extrair_duais_em_dataframe(modelo.model)
            df_duais["caso"] = i
            df_duais.to_csv("results/csv/duais.csv", mode="a", header=not bool(i), index=False)

        # Extrair resultados
        resultado = extrair_resultados(modelo, system=sistema, elemento_removido=linha.id)
        resultados.append(resultado)

    return pd.concat(resultados, ignore_index=True)
