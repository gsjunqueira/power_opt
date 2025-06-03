"""
Módulo `transporte`

Insere as variáveis e restrições de fluxo de potência linearizado (DC) no modelo de despacho.

Modela o transporte de energia entre barras com base em parâmetros como susceptância e
diferença angular, garantindo coerência entre geração, carga e fluxo.

Autor: Giovani Santiago Junqueira
"""

__author__ = "Giovani Santiago Junqueira"

from pyomo.environ import Constraint

def aplicar_transporte(model, system):
    """
    Aplica a modelagem de transporte de energia elétrica.

    Esta função define a variável de fluxo de potência F (caso habilitado) 
    e aplica a restrição de balanço de potência nas barras ou no sistema como um todo.

    A lógica segue as seguintes regras:
    - Se a flag `considerar_fluxo` estiver ativada:
        • Modela o fluxo de potência por linha (variável F).
        • Aplica o balanço de potência individualmente por barra.
    - Caso contrário:
        • Aplica um único balanço global para todo o sistema.
    - Se `usar_deficit` estiver ativado:
        • O déficit entra no balanço como variável adicional.

    Args:
        model (ConcreteModel): O modelo Pyomo onde as variáveis e restrições são definidas.
        system (FullSystem): O sistema elétrico contendo os dados e configurações.

    Returns:
        None
    """
    usar_fluxo = system.config.get("considerar_fluxo", False)
    usar_deficit = system.config.get("usar_deficit", False)

    if usar_fluxo:
        # model.F = Var(model.L, model.T, domain=Reals)

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
            deficit = model.Deficit[b, t] if usar_deficit and (b, t) in model.D else 0

            return geracao + entrada - saida + deficit == carga

        model.balanco = Constraint(model.B, model.T, rule=balanco_por_barra)

        # Limites do fluxo por linha
        model.restr_fluxo_sup = Constraint(model.L, model.T,
                                           rule=lambda m, l, t: m.F[l, t] <= m.f_max[l])
        model.restr_fluxo_inf = Constraint(model.L, model.T,
                                           rule=lambda m, l, t: m.F[l, t] >= -m.f_max[l])


    else:
        def balanco_total(model, t):
            """
            Balanço de potência total do sistema, somando toda geração e carga.
            """
            total_geracao = sum(model.P[g, t] for g in model.G)
            total_carga = sum(model.demanda[b, t] for b in model.B)

            if usar_deficit:
                total_deficit = sum(model.Deficit[b, t] for (b, tp) in model.D if tp == t)
                return total_geracao + total_deficit == total_carga
            else:
                return total_geracao == total_carga

        model.balanco = Constraint(model.T, rule=balanco_total)
