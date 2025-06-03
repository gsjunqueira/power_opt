"""
Módulo `rampa`

Define as restrições de rampa para os geradores no modelo de despacho.

Garante que a variação da geração ativa entre períodos consecutivos respeite
os limites máximos definidos para cada gerador.

Autor: Giovani Santiago Junqueira
"""

__author__ = "Giovani Santiago Junqueira"

from pyomo.environ import Constraint


def aplicar_rampa(model, system):
    """
    Adiciona as restrições de rampa ao modelo, se disponíveis no sistema.

    Args:
        model (ConcreteModel): Modelo Pyomo em construção.
        system (FullSystem): Objeto com os dados do sistema, contendo rampas por gerador.
    """

    if not system.config.get("considerar_rampa", False):
        return  # Flag desativada, não aplica restrições de rampa

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
