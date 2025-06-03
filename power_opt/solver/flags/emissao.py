"""
Módulo `emissao`

Define a contribuição das emissões de CO₂ para a função objetivo no modelo de despacho.

Aplica penalidades associadas a cada gerador com fator de emissão especificado,
sendo o impacto ponderado por um parâmetro `delta`.

Autor: Giovani Santiago Junqueira
"""

__author__ = "Giovani Santiago Junqueira"

from pyomo.environ import Expression

def aplicar_emissao(model, system):
    """
    Adiciona a expressão de custo da função objetivo considerando emissões de CO₂.

    Args:
        model (ConcreteModel): Modelo Pyomo.
        system (FullSystem): Sistema com dados e configuração.

    Returns:
        Expression: expressão a ser incorporada na FOB.
    """
    custo_base = sum(
        model.P[g, t] * model.custo[g]
        for g in model.G if not g.startswith("GF")
        for t in model.T
    )

    if not system.config.get("considerar_emissao", False):
        model.fob_emissao = Expression(expr=custo_base)
        return model.fob_emissao

    penal_emissao = sum(
        model.P[g, t] * model.emissao[g]
        for g in model.G
        for t in model.T
    )

    fob_emissao = model.delta * custo_base + \
                  (1 - model.delta) * model.custo_emissao * penal_emissao

    model.fob_emissao = Expression(expr=fob_emissao)

    return model.fob_emissao
