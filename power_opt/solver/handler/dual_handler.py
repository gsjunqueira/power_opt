"""
Módulo `dual_handler`

Responsável por extrair, armazenar e organizar os multiplicadores de Lagrange
(variáveis duais) associados às restrições do modelo de otimização.

Autor: Giovani Santiago Junqueira
"""

__author__ = "Giovani Santiago Junqueira"

import os
import csv
import pandas as pd
from pyomo.environ import Constraint

def extrair_duais_em_dataframe(model) -> pd.DataFrame:
    """
    Retorna os multiplicadores de Lagrange das restrições, caso o solver seja GLPK.

    Args:
        model: Modelo Pyomo resolvido.

    Returns:
        pd.DataFrame: Tabela contendo nome da restrição, índice e valor dual.
    """
    if not hasattr(model, "dual"):
        raise RuntimeError("As variáveis duais não estão disponíveis. "
                           "Certifique-se de usar o solver GLPK e configurar 'Suffix' como IMPORT.")

    dados = []
    for constr in model.component_objects(Constraint, active=True):
        nome = constr.name
        for idx in constr:
            dual = model.dual.get(constr[idx], None)
            if dual is not None:
                dados.append({
                    "restricao": nome,
                    "indice": idx if isinstance(idx, tuple) else (idx,),
                    "dual": dual
                })

    return pd.DataFrame(dados)

def imprimir_duais(model):
    """
    Imprime os valores dos multiplicadores de Lagrange (duais) para cada restrição.

    Args:
        model: Modelo Pyomo resolvido.
    """
    if not hasattr(model, "dual"):
        print("❌ Atributo 'dual' não encontrado. Certifique-se de que o solver GLPK foi utilizado.")
        return

    print("\n🔎 DUALS (Multiplicadores de Lagrange):")
    for constr in model.component_objects(Constraint, active=True):
        for index in constr:
            dual_val = model.dual.get(constr[index], None)
            print(f"{constr.name}[{index}] = {dual_val}")


def exportar_duais_csv(model, caminho_csv: str):
    """
    Exporta os valores dos duais para um arquivo CSV único.

    Args:
        model: Modelo Pyomo resolvido.
        caminho_csv (str): Caminho completo para o CSV.
    """
    if not hasattr(model, "dual"):
        raise RuntimeError(
            "⚠️ Multiplicadores de Lagrange não foram carregados (modelo.dual inexistente).")

    with open(caminho_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["restricao", "indice", "valor_dual"])
        for nome, componente in model.component_map(Constraint, active=True).items():
            for indice in componente:
                restricao = componente[indice]
                if restricao.active:
                    dual = model.dual.get(restricao, 0.0)
                    writer.writerow([nome, indice, dual])


def exportar_duais_csv_acumulado(model, caminho_csv: str, id_caso: str):
    """
    Exporta os duais para um CSV acumulado com identificador de caso (ideal para
    múltiplas simulações).

    Args:
        model: Modelo Pyomo resolvido.
        caminho_csv (str): Caminho do arquivo CSV (criado se não existir).
        id_caso (str): Identificador único para o caso.
    """
    if not hasattr(model, "dual"):
        raise RuntimeError(
            "⚠️ Multiplicadores de Lagrange não foram carregados (modelo.dual inexistente).")

    escrever_cabecalho = not os.path.exists(caminho_csv)

    with open(caminho_csv, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if escrever_cabecalho:
            writer.writerow(["caso", "restricao", "indice", "valor_dual"])

        for nome, componente in model.component_map(Constraint, active=True).items():
            for indice in componente:
                restricao = componente[indice]
                if restricao.active:
                    dual = model.dual.get(restricao, 0.0)
                    writer.writerow([id_caso, nome, indice, dual])
