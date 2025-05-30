"""
Módulo `result_handler`

Responsável por extrair os resultados do modelo Pyomo após a otimização e organizá-los 
em estruturas compatíveis com análises e exportação. Este módulo separa a lógica de 
extração de dados da definição e solução do modelo, promovendo clareza e reuso.

Funções principais:
- extrair_resultados(model, system): retorna um dicionário com dados organizados.
- salvar_resultados_em_csv(resultados: dict, caminho: str): salva os dados em CSV.

Autor: Giovani Santiago Junqueira
"""

from pyomo.environ import value
import pandas as pd


def extrair_resultados(model, system):
    """
    Extrai os resultados do modelo Pyomo resolvido.

    Args:
        model: Modelo Pyomo resolvido.
        system: Objeto do sistema contendo metadados como base de potência.

    Returns:
        dict: Resultados organizados com chaves como 'FOB', 'geracao', 'fluxo', etc.
    """
    base = system.base_power
    resultados = {"FOB": value(model.objetivo) * base}

    # Extração da geração por gerador e tempo
    resultados["geracao"] = {
        (g, t): value(model.P[g, t]) * base
        for g in model.G
        for t in model.T
        if (g, t) in model.P
    }

    # Extração dos fluxos de linha
    if hasattr(model, "F"):
        resultados["fluxo"] = {
            (l, t): value(model.F[l, t]) * base
            for l in model.L
            for t in model.T
            if (l, t) in model.F
        }

    # Extração de déficit, se existir
    if hasattr(model, "Deficit"):
        resultados["deficit"] = {
            (b, t): value(model.Deficit[b, t]) * base
            for b, t in model.Deficit
        }

    return resultados


def salvar_resultados_em_csv(resultados, caminho_csv):
    """
    Salva os resultados extraídos em formato CSV plano.

    Args:
        resultados (dict): Dicionário retornado por extrair_resultados().
        caminho_csv (str): Caminho completo do arquivo CSV de destino.
    """
    linhas = []
    for (g, t), valor in resultados.get("geracao", {}).items():
        linhas.append({
            "tipo": "geracao",
            "elemento": g,
            "tempo": t,
            "valor": valor
        })

    for (l, t), valor in resultados.get("fluxo", {}).items():
        linhas.append({
            "tipo": "fluxo",
            "elemento": l,
            "tempo": t,
            "valor": valor
        })

    for (b, t), valor in resultados.get("deficit", {}).items():
        linhas.append({
            "tipo": "deficit",
            "elemento": b,
            "tempo": t,
            "valor": valor
        })

    # Adiciona a FOB como uma linha única
    linhas.append({
        "tipo": "FOB",
        "elemento": "total",
        "tempo": None,
        "valor": resultados.get("FOB", 0.0)
    })

    df = pd.DataFrame(linhas)
    df.to_csv(caminho_csv, index=False)
