"""
Módulo `emissao`

Define a contribuição das emissões de CO₂ e o custo base da função objetivo.

Toda a lógica, incluindo casos com ou sem emissão, é encapsulada aqui, mantendo
a coesão e evitando a dispersão da lógica no model_builder.

Autor: Giovani Santiago Junqueira
"""

__author__ = "Giovani Santiago Junqueira"

from pyomo.environ import Param, Expression, NonNegativeReals
from power_opt.solver.flags import flag_ativa

def aplicar_emissao(model, system):
    """
    Aplica a penalidade de emissão à função objetivo, ponderada por delta,
    apenas se a flag `considerar_emissao` estiver ativa.

    Args:
        model (ConcreteModel): Modelo Pyomo.
        system (FullSystem): Sistema com dados e configurações.
    """
    if flag_ativa("emissao", system):
        model.custo_base = Expression(
            expr=sum(
                model.P[g, t] * model.custo[g]
                for g in model.G if not g.startswith("GF")
                for t in model.T
            )
        )

        model.emissao = Param(model.G,
            initialize={g.id: g.emission for bus in system.buses.values() for g in bus.generators},
            within=NonNegativeReals
        )

        model.custo_emissao = Param(
            initialize=system.config["custo_emissao"],
            within=NonNegativeReals
        )

        penal_emissao = sum(
            model.P[g, t] * model.emissao[g]
            for g in model.G
            for t in model.T
        )

        model.fob_emissao = Expression(
            expr=model.delta * model.custo_base +
                (1 - model.delta) * model.custo_emissao * penal_emissao
        )
        express = model.fob_emissao
    else:
        model.fob_emissao = Expression(
            expr=sum(
                model.P[g, t] * model.custo[g]
                for g in model.G if not g.startswith("GF")
                for t in model.T
            )
        )
        express = model.fob_emissao
    return express
