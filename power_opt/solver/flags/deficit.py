"""
Módulo `deficit`

Define a modelagem do corte de carga (déficit) no modelo de despacho.

Adiciona variáveis de déficit associadas a cada barra e período de tempo, bem como
restrições que permitem que a carga não atendida seja penalizada na função objetivo.

Autor: Giovani Santiago Junqueira
"""

__author__ = "Giovani Santiago Junqueira"

from pyomo.environ import Constraint, Expression

def aplicar_deficit(model, system):
    """
    Aplica a modelagem de déficit com base na configuração do sistema.

    Args:
        model (ConcreteModel): Modelo Pyomo em construção.
        system (FullSystem): Objeto que contém os dados do sistema.
    
    Returns:
        Expression: parcela de custo associada ao déficit (real ou via gerador fictício).
    """
    usar_deficit = system.config.get("usar_deficit", False)

    if usar_deficit:
        # # Define a variável Deficit
        # if hasattr(model, 'Deficit'):
        #     model.del_component('Deficit')
        # model.Deficit = Var(model.B, model.T, domain=NonNegativeReals)

        # Restrições de limite máximo de déficit
        def limite_deficit_rule(model, b, t):
            if (b, t) in model.D:
                return model.Deficit[b, t] <= model.max_deficit[b, t]
            return Constraint.Skip

        model.limite_deficit = Constraint(model.B, model.T, rule=limite_deficit_rule)

        # Expressão de custo do déficit
        model.custo_deficit = Expression(
            expr=sum(
                model.Deficit[b, t] * model.cost_deficit[b, t]
                for (b, t) in model.D
            )
        )
    else:
        # Não usamos variável de déficit, mas o custo dos geradores fictícios deve ser considerado
        model.custo_deficit = Expression(
            expr=sum(
                model.P[g, t] * model.custo[g]
                for g in model.G if g.startswith("GF")
                for t in model.T
            )
        )

    return model.custo_deficit
