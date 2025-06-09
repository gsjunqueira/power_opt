"""
Módulo `perdas`

Implementa a lógica para cálculo iterativo de perdas nas linhas de transmissão, considerando
as duas abordagens: transporte (fluxo como variável) e fluxo DC (fluxo como expressão baseada em θ).

As perdas são redistribuídas como carga adicional nas barras extremas. O processo é repetido
até convergência.

Autor: Giovani Santiago Junqueira
"""

__author__ = "Giovani Santiago Junqueira"

import os
from typing import Dict, Tuple
from pyomo.environ import value, ConcreteModel, Suffix
from pyomo.opt import SolverFactory
from power_opt.solver.flags import flag_ativa, safe_del

def inicializar_perdas(system) -> Dict[Tuple[str, int], float]:
    """
    Inicializa o dicionário de perdas por barra e tempo com valores zero.
    """
    return {
        (bus, t): 0.0
        for bus in system.buses
        for t in range(len(system.load_profile))
    }

def armazenar_carga_base(system) -> Dict[Tuple[str, int], float]:
    """
    Armazena a carga original de cada barra e tempo antes da introdução das perdas.
    """
    return {
        (load.bus, t): load.demand
        for t, cargas in enumerate(system.load_profile)
        for load in cargas
    }

def calcular_perdas(model, system) -> Tuple[Dict[Tuple[str, int], float], float]:
    """
    Calcula as perdas por linha e redistribui como carga em cada barra.
    Considera o modo de fluxo utilizado (transporte ou fluxo DC).
    """
    perdas = inicializar_perdas(system)
    perda_total = 0.0

    for linha in system.lines:
        g = value(model.conductance[linha.id])
        b = value(model.susceptance[linha.id])

        for t in list(model.T):
            if flag_ativa("fluxo_dc", system):
                theta_i = value(model.theta[linha.from_bus, t])
                theta_j = value(model.theta[linha.to_bus, t])
                perda = g * ((theta_i - theta_j) ** 2)
            else:
                fluxo = value(model.F[linha.id, t])
                perda = g * ((fluxo / b) ** 2 if b != 0 else 0.0)

            perda_total += perda
            perdas[(linha.from_bus, t)] += 0.5 * perda
            perdas[(linha.to_bus, t)] += 0.5 * perda

    return perdas, perda_total

def atualizar_cargas_com_perdas(system, carga_base: Dict[Tuple[str, int], float],
                                perdas: Dict[Tuple[str, int], float]) -> None:
    """
    Atualiza a carga total de cada barra somando a perda equivalente.
    """
    for t, cargas in enumerate(system.load_profile):
        for carga in cargas:
            chave = (carga.bus, t)
            carga.demand = carga_base[chave] + perdas[chave]

def calcular_diferenca_perdas(p1: Dict[Tuple[str, int], float],
                              p2: Dict[Tuple[str, int], float]) -> float:
    """
    Compara perdas entre duas iterações.
    """
    return sum(abs(p2[k] - p1[k]) for k in p1)

def aplicar_perdas_iterativamente(modelo, solver_name="highs",
                                  tee=False, max_iter=40, epsilon=1e-16):
    """
    Executa o processo iterativo de cálculo e redistribuição de perdas por linha no sistema.

    Esta função é ativada apenas se a flag `considerar_perdas` estiver ligada.
    """
    if flag_ativa("perdas", modelo.system) and (
        flag_ativa("fluxo_dc", modelo.system) or flag_ativa("transporte", modelo.system)):
        system = modelo.system
        model = modelo.model
        modelo.set_resolvendo_perdas = True
        iteracao = 0
        convergiu = False

        carga_base = armazenar_carga_base(system)
        perdas_ant = inicializar_perdas(system)

        while not convergiu and iteracao < max_iter:
            if solver_name.lower() == 'glpk':
                safe_del(model, 'dual')
                model.dual = Suffix(direction=Suffix.IMPORT)
                os.environ["PATH"] = "/opt/homebrew/bin:" + os.environ["PATH"]
                solver = SolverFactory(solver_name, executable="/opt/homebrew/bin/glpsol")
            else:
                solver = SolverFactory(solver_name)

            solver.solve(model, tee=tee)

            print(f"🌀 Iteração atual = {iteracao}")
            perdas_atuais, perda_total = calcular_perdas(model, system)
            atualizar_cargas_com_perdas(system, carga_base, perdas_atuais)

            delta = calcular_diferenca_perdas(perdas_ant, perdas_atuais)

            if delta < epsilon:
                convergiu = True
                modelo.set_perdas_finais = {
                    "perda_linha": perdas_atuais,
                    "perda_total": perda_total,
                }
            else:
                perdas_ant = perdas_atuais.copy()
                modelo.model = ConcreteModel()
                if solver_name.lower() == 'glpk':
                    safe_del(modelo.model, 'dual')
                    modelo.model.dual = Suffix(direction=Suffix.IMPORT)
                modelo.build(**modelo.config_flags)

            iteracao += 1

        if not convergiu:
            raise RuntimeError(
                "❌ O processo de perdas não convergiu após o número máximo de iterações.")

        modelo.model = ConcreteModel()
        if solver_name.lower() == 'glpk':
            safe_del(modelo.model, 'dual')
            modelo.model.dual = Suffix(direction=Suffix.IMPORT)
        modelo.model_built = False
        modelo.build(**modelo.config_flags)
        solver = SolverFactory(solver_name)
        solver.solve(modelo.model, tee=tee)
        modelo.set_resolvendo_perdas = False
    else:
        if solver_name == "glpk":
            safe_del(modelo.model, "dual")
            modelo.model.dual = Suffix(direction=Suffix.IMPORT)
            os.environ["PATH"] = "/opt/homebrew/bin:" + os.environ["PATH"]
            solver = SolverFactory(solver_name, executable="/opt/homebrew/bin/glpsol")
        else:
            solver = SolverFactory(solver_name)

        solver.solve(modelo.model, tee=tee)
