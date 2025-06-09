"""
Módulo `result_handler`

Consolida os resultados obtidos nas simulações de despacho ótimo, organiza os
dados em formatos estruturados (DataFrame, CSV) e prepara as saídas conforme
diferentes configurações de cenário e variáveis ativadas.

Autor: Giovani Santiago Junqueira
"""

__author__ = "Giovani Santiago Junqueira"

from collections.abc import Iterable
from pyomo.environ import value
import pandas as pd

def flatten(lista):
    """
    Achata uma lista de listas em uma lista simples.
    Ignora strings e DataFrames, que são iteráveis mas não devem ser expandidos.
    """
    for item in lista:
        if isinstance(item, pd.DataFrame):
            yield item
        elif isinstance(item, Iterable) and not isinstance(item, (str, bytes)):
            yield from flatten(item)
        else:
            raise TypeError(f"Tipo inválido na lista de resultados: {type(item)}")

def extrair_resultados(model, system, elemento_removido="None"):
    """
    Extrai os resultados do modelo Pyomo resolvido e retorna DataFrame com ID único.

    Args:
        model: Instância de PyomoSolver com o modelo resolvido.
        system: Instância FullSystem com dados e configuração.
        execucao (int or str, opcional): Número ou código da execução atual.
        elemento_removido (str): Elemento removido na análise N-1, se houver.

    Returns:
        pd.DataFrame: DataFrame com resultados e identificador único da simulação.
    """
    base = system.base_power

    delta = int(system.config.get("delta", 0) * 100)
    emissao = "V" if system.config.get("emissao", False) else "F"
    transporte = "V" if system.config.get("transporte", False) else "F"
    fluxo_dc = "V" if system.config.get("fluxo_dc", False) else "F"
    perdas = "V" if system.config.get("perdas", False) else "F"
    rampa = "V" if system.config.get("rampa", False) else "F"
    deficit = "V" if system.config.get("deficit", False) else "F"
    if fluxo_dc == "V":
        transporte = "F"
    id_simulacao = f"{delta}{emissao}{transporte}{fluxo_dc}{perdas}{rampa}{deficit}"
    id_remocao = elemento_removido if elemento_removido is not None else None

    id_simulacao += f"_{id_remocao}"

    resultados = []

    # FOB
    resultados.append({
        "simulacao": id_simulacao,
        "tipo": "FOB",
        "id": "total",
        "tempo": None,
        "valor": value(model.model.objetivo)
    })

    # Geração
    for (g, t) in model.model.P:
        resultados.append({
            "simulacao": id_simulacao,
            "tipo": "geracao",
            "id": g,
            "tempo": t,
            "valor": value(model.model.P[g, t]) * base
        })

    # Fluxo
    if hasattr(model.model, "F"):
        for (l, t) in model.model.F:
            resultados.append({
                "simulacao": id_simulacao,
                "tipo": "fluxo",
                "id": l,
                "tempo": t,
                "valor": value(model.model.F[l, t]) * base
            })

    # Déficit
    if hasattr(model.model, "Deficit"):
        for (b, t) in model.model.Deficit:
            resultados.append({
                "simulacao": id_simulacao,
                "tipo": "deficit",
                "id": b,
                "tempo": t,
                "valor": value(model.model.Deficit[b, t]) * base
            })

    # Perdas por linha
    if hasattr(model.model, "perda_linha"):
        for (l, t) in model.model.perda_linha:
            resultados.append({
                "simulacao": id_simulacao,
                "tipo": "perda_linha",
                "id": l,
                "tempo": t,
                "valor": value(model.model.perda_linha[l, t]) * base
            })

    # Perdas por barra
    if hasattr(model.model, "perda_barra"):
        for (b, t) in model.model.perda_barra:
            resultados.append({
                "simulacao": id_simulacao,
                "tipo": "perda_barra",
                "id": b,
                "tempo": t,
                "valor": value(model.model.perda_barra[b, t]) * base
            })

    # Perda total
    if hasattr(model.model, "perda_total"):
        for t in model.model.T:
            resultados.append({
                "simulacao": id_simulacao,
                "tipo": "perda_total",
                "id": "sistema",
                "tempo": t,
                "valor": value(model.model.perda_total[t]) * base
            })

    return pd.DataFrame(resultados)


def salvar_resultados_em_csv(lista_resultados, caminho_csv):
    """
    Salva os resultados de múltiplas simulações em um único CSV consolidado.

    Args:
        lista_resultados (list[pd.DataFrame]): Lista de DataFrames retornados por
        `extrair_resultados`.
        caminho_csv (str): Caminho completo para o arquivo CSV final.
    """
    lista = list(flatten(lista_resultados))
    df_consolidado = pd.concat(lista, ignore_index=True)
    df_consolidado.to_csv(caminho_csv, index=False)
