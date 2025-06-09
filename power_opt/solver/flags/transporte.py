"""
Módulo `transporte`

Insere as variáveis e restrições de fluxo de potência linearizado (DC) no modelo de despacho.

Modela o transporte de energia entre barras com base em parâmetros como susceptância e
diferença angular, garantindo coerência entre geração, carga e fluxo.

Autor: Giovani Santiago Junqueira
"""

__author__ = "Giovani Santiago Junqueira"

from pyomo.environ import Constraint, Param, Reals, NonNegativeReals, Var
from power_opt.solver.flags import flag_ativa, safe_del

def aplicar_transporte(model, system):
    """
    Aplica a modelagem de transporte de energia elétrica com base na flag `usar_fluxo`.

    Quando ativado:
    - Define os parâmetros de linha: susceptância, condutância e limite de fluxo (f_max).
    - Define a variável de fluxo `F`.
    - Aplica o balanço de potência por barra considerando geração, fluxo e déficit.
    - Aplica restrições de limite de fluxo por linha.

    Args:
        model (ConcreteModel): O modelo Pyomo onde as variáveis e restrições são definidas.
        system (FullSystem): O sistema elétrico contendo os dados e configurações.
    """

    if flag_ativa("transporte", system):
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

        safe_del(model, 'F')
        model.F = Var(model.L, model.T, domain=Reals)

        def balanco_por_barra(model, b, t):
            """
            Balanço de potência por barra, com entrada e saída de fluxo, geração e déficit.
            """
            destination = {linha.id: linha.to_bus for linha in system.lines}
            origin = {linha.id: linha.from_bus for linha in system.lines}
            geradores_na_barra = [g.id for g in system.get_bus(b).generators]
            geracao = sum(model.P[g, t] for g in geradores_na_barra)

            carga = model.demanda[b, t] if (b, t) in model.demanda else 0
            entrada = sum(model.F[l, t] for l in model.L if destination[l] == b)
            saida = sum(model.F[l, t] for l in model.L if origin[l] == b)
            deficit = model.Deficit[b, t] if flag_ativa("deficit", system
                                                        ) and (b, t) in model.D else 0

            return geracao + entrada - saida + deficit == carga

        model.balanco = Constraint(model.B, model.T, rule=balanco_por_barra)

        model.restr_fluxo_sup = Constraint(
            model.L, model.T, rule=lambda m, l, t: m.F[l, t] <= m.f_max[l]
        )
        model.restr_fluxo_inf = Constraint(
            model.L, model.T, rule=lambda m, l, t: m.F[l, t] >= -m.f_max[l]
        )
    else:
        def balanco_total(model, t):
            """
            Balanço de potência total do sistema, somando toda geração, carga e déficit.
            """
            total_geracao = sum(model.P[g, t] for g in model.G)
            total_carga = sum(model.demanda[b, t] for b in model.B)

            if flag_ativa("deficit", system):
                total_deficit = sum(model.Deficit[b, t] for (b, tp) in model.D if tp == t)
                express = total_geracao + total_deficit == total_carga
            else:
                express = total_geracao == total_carga
            return express

        model.balanco = Constraint(model.T, rule=balanco_total)
