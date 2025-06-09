"""
Módulo `rampa`

Define as restrições de rampa para os geradores no modelo de despacho.

Garante que a variação da geração ativa entre períodos consecutivos respeite
os limites máximos definidos para cada gerador.

Autor: Giovani Santiago Junqueira
"""

__author__ = "Giovani Santiago Junqueira"

from pyomo.environ import Constraint, Param, NonNegativeReals
from power_opt.solver.flags import flag_ativa

def aplicar_rampa(model, system):
    """
    Adiciona parâmetros e restrições de rampa ao modelo Pyomo.

    Args:
        model (ConcreteModel): Modelo Pyomo em construção.
        system (FullSystem): Objeto com os dados do sistema, contendo rampas por gerador.
    """
    if flag_ativa("rampa", system):
        rampas = {
            g.id: g.ramp
            for bus in system.buses.values()
            for g in bus.generators
            if hasattr(g, "ramp") and g.ramp is not None
        }
        model.rampa = Param(
            model.G,
            initialize=rampas,
            within=NonNegativeReals,
            default=0.0
    )

        def rampa_inf_rule(model, g, t):
            """
            Restrição de rampa inferior: limite na redução de geração entre períodos consecutivos.
            """
            if t == 0:
                return Constraint.Skip
            return model.P[g, t - 1] - model.P[g, t] <= model.rampa[g]

        def rampa_sup_rule(model, g, t):
            """
            Restrição de rampa superior: limite no aumento de geração entre períodos consecutivos.
            """
            if t == 0:
                return Constraint.Skip
            return model.P[g, t] - model.P[g, t - 1] <= model.rampa[g]

        model.rampa_inf = Constraint(model.G, model.T, rule=rampa_inf_rule)
        model.rampa_sup = Constraint(model.G, model.T, rule=rampa_sup_rule)
