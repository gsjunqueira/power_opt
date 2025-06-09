"""
Módulo `fluxo_dc`

Modela o fluxo de potência DC com base na diferença angular entre barras.

Define as variáveis de ângulo (theta), calcula o fluxo F como expressão dependente 
de susceptância e diferença angular, e aplica as restrições de fluxo máximo por linha.

Autor: Giovani Santiago Junqueira
"""

__author__ = "Giovani Santiago Junqueira"

from pyomo.environ import Constraint, Expression, Var, Param, Reals, NonNegativeReals, Any
from power_opt.solver.flags import flag_ativa, safe_del
from power_opt.solver.flags.transporte import aplicar_transporte

def aplicar_fluxo_dc(model, system):
    """
    Aplica o modelo de fluxo DC no sistema de despacho.

    - Define a variável `theta` (ângulo por barra).
    - Define `F` como expressão: F = susceptance * (theta_i - theta_j).
    - Aplica restrições de fluxo superior e inferior por linha.

    Args:
        model (ConcreteModel): Modelo Pyomo.
        system (FullSystem): Sistema com dados e configuração.
    """
    if flag_ativa("fluxo_dc", system):
        model.susceptance = Param(
            model.L,
            initialize={linha.id: linha.susceptance for linha in system.lines},
            within=Reals
        )
        model.conductance = Param(
            model.L,
            initialize={linha.id: linha.conductance for linha in system.lines},
            within=Reals
        )
        model.f_max = Param(
            model.L,
            initialize={linha.id: linha.limit for linha in system.lines},
            within=NonNegativeReals
        )
        model.de = Param(
            model.L,
            initialize={linha.id: linha.from_bus for linha in system.lines},
            within=Any
        )
        model.para = Param(
            model.L,
            initialize={linha.id: linha.to_bus for linha in system.lines},
            within=Any
        )

        safe_del(model, 'theta')
        safe_del(model, 'F')

        model.theta = Var(model.B, model.T, domain=Reals)

        model.F = Expression(model.L, model.T, rule=lambda m, l, t:
            m.susceptance[l] * (m.theta[m.de[l], t] - m.theta[m.para[l], t])
        )

        model.restr_fluxo_sup = Constraint(
            model.L, model.T, rule=lambda m, l, t: m.F[l, t] <= m.f_max[l]
        )
        model.restr_fluxo_inf = Constraint(
            model.L, model.T, rule=lambda m, l, t: m.F[l, t] >= -m.f_max[l]
        )
        def balanco_por_barra(model, b, t):
            """
            Balanço de potência por barra para fluxo DC.

            Soma geração local, entrada de fluxo, subtrai saída e considera déficit se ativado.
            """
            geradores = [g.id for g in system.get_bus(b).generators]
            geracao = sum(model.P[g, t] for g in geradores)

            entrada = sum(model.F[l, t] for l in model.L if model.para[l] == b)
            saida = sum(model.F[l, t] for l in model.L if model.de[l] == b)

            carga = model.demanda[b, t] if (b, t) in model.demanda else 0
            deficit = (
                model.Deficit[b, t]
                if flag_ativa("deficit", system) and (b, t) in model.D
                else 0
            )

            return geracao + entrada - saida + deficit == carga
        safe_del(model, "balanco")
        model.balanco = Constraint(model.B, model.T, rule=balanco_por_barra)
    else:
        aplicar_transporte(model, system)
