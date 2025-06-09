"""
Módulo `deficit`

Define a modelagem do corte de carga (déficit) no modelo de despacho.

Adiciona variáveis, restrições e expressão de penalidade associadas ao não atendimento.

Autor: Giovani Santiago Junqueira
"""

__author__ = "Giovani Santiago Junqueira"

from pyomo.environ import Constraint, Expression, Param, Var, NonNegativeReals, Set
from power_opt.solver.flags import flag_ativa, safe_del

def aplicar_deficit(model, system):
    """
    Aplica a modelagem do déficit ao modelo Pyomo.

    Define os parâmetros, variáveis, restrições e a expressão de custo associada ao déficit.

    Args:
        model (ConcreteModel): Modelo Pyomo.
        system (FullSystem): Dados do sistema elétrico.
    """
    if flag_ativa("deficit", system):
        model.GF = Set(initialize=[g.id for  bus in system.buses.values()
                                   for g in bus.generators if g.id.startswith("GF")])
        model.restringe_GF = Constraint(model.GF, model.T, rule=lambda m, g, t: m.P[g, t] == 0)
        model.D = Set(dimen=2, initialize=lambda m: [(d.bus, d.period) for d in system.deficits])

        model.cost_deficit = Param(
            model.B, model.T,
            initialize={(d.bus, d.period): d.cost for d in system.deficits},
            within=NonNegativeReals,
            default=0.0,
        )

        model.max_deficit = Param(
            model.B, model.T,
            initialize={(d.bus, d.period): d.max_deficit for d in system.deficits},
            within=NonNegativeReals,
            default=0.0,
        )

        safe_del(model, "Deficit")
        model.Deficit = Var(model.B, model.T, domain=NonNegativeReals)

        def limite_deficit_rule(model, b, t):
            return model.Deficit[b, t] <= model.max_deficit[b, t]

        model.limite_deficit = Constraint(model.B, model.T, rule=limite_deficit_rule)

        model.custo_deficit = Expression(
            expr=sum(
                model.Deficit[b, t] * model.cost_deficit[b, t]
                for b in model.B
                for t in model.T
            )
        )
        express = model.custo_deficit
    else:
        model.custo_deficit = Expression(
            expr=sum(
                model.P[g, t] * model.custo[g]
                for g in model.G if g.startswith("GF")
                for t in model.T
            )
        )
        express = model.custo_deficit
    return express
