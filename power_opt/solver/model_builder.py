"""
Módulo `model_builder`

Define as funções responsáveis por construir o modelo de despacho elétrico no Pyomo,
de forma modular e sequencial. A construção segue a ordem lógica: conjuntos,
parâmetros, variáveis, restrições e função objetivo.

Esse módulo centraliza toda a lógica de modelagem, isolando as implementações
condicionais por meio de funções auxiliares nos módulos de flags.

Autor: Giovani Santiago Junqueira
"""

__author__ = "Giovani Santiago Junqueira"

from pyomo.environ import (
    Constraint, NonNegativeReals, Objective, Param,
    Set, Var, minimize, Suffix)
from power_opt.solver.flags import (
    aplicar_deficit, aplicar_emissao, aplicar_rampa, aplicar_fluxo_dc, safe_del)


def definir_conjuntos(model, system):
    """
    Define os conjuntos do modelo a partir do sistema fornecido.

    Args:
        model (ConcreteModel): Modelo Pyomo.
        system (FullSystem): Objeto que contém os dados do sistema elétrico.
    """
    model.G = Set(initialize=[gen.id for bus in system.buses.values() for gen in bus.generators])
    model.B = Set(initialize=list(system.buses.keys()))
    model.T = Set(initialize=range(len(system.load_profile)))
    model.L = Set(initialize=[linha.id for linha in system.lines])

def definir_parametros(model, system):
    """
    Define os parâmetros do modelo a partir do sistema fornecido.

    Args:
        model (ConcreteModel): Modelo Pyomo.
        system (FullSystem): Objeto que contém os dados do sistema elétrico.
    """

    model.custo = Param(model.G,
        initialize={g.id: g.cost for bus in system.buses.values() for g in bus.generators},
        within=NonNegativeReals,
    )
    model.gmin = Param(model.G,
        initialize={g.id: g.gmin for bus in system.buses.values() for g in bus.generators}
    )
    model.gmax = Param(model.G,
        initialize={g.id: g.gmax for bus in system.buses.values() for g in bus.generators}
    )
    model.demanda = Param(model.B, model.T,
        initialize={(load.bus, t): load.demand for t, cargas in enumerate(
            system.load_profile) for load in cargas}
    )
    model.base = Param(initialize=system.base_power)
    model.delta = Param(initialize=system.config.get("delta", 1))

def definir_variaveis(model):
    """
    Define as variáveis de decisão do modelo.

    Args:
        model (ConcreteModel): Modelo Pyomo.
        system (FullSystem): Objeto que contém os dados do sistema elétrico.
    """

    safe_del(model, 'dual')
    safe_del(model, 'P')

    model.P = Var(model.G, model.T, domain=NonNegativeReals)
    model.dual = Suffix(direction=Suffix.IMPORT)

def definir_restricoes(model, system):
    """
    Define as restrições do modelo de despacho.

    Args:
        model (ConcreteModel): Modelo Pyomo.
        system (FullSystem): Objeto que contém os dados do sistema elétrico.
    """

    def limites_geracao_rule(model, g, t):
        """
        Restrição de limites inferior e superior de geração para cada gerador e tempo.
        """
        return (model.gmin[g], model.P[g, t], model.gmax[g])
    model.limites = Constraint(model.G, model.T, rule=limites_geracao_rule)


    # Parte associada ao déficit ou geradores fictícios
    aplicar_deficit(model, system)

    # Aplica lógica condicional de rampas se configurada
    aplicar_rampa(model, system)

    # Parte do custo total e da penalidade por emissão
    aplicar_emissao(model, system)

    # Aplica lógica condicional de fluxo dc ou transporte se configurada
    aplicar_fluxo_dc(model, system)


def definir_objetivo(model):
    """
    Define a função objetivo do modelo de otimização.

    A função objetivo pondera o custo de geração, a penalidade por emissão e o custo do déficit,
    combinando as expressões previamente definidas nos módulos especializados.

    Args:
        model (ConcreteModel): Modelo Pyomo.
        system (FullSystem): Objeto que contém os dados do sistema elétrico.
    """

    model.objetivo = Objective(
        expr=model.fob_emissao + model.custo_deficit,
        sense=minimize
    )

def build_model(model, system):
    """
    Esta função constrói o modelo Pyomo de forma modular e ordenada:

    1. Conjuntos
    2. Parâmetros
    3. Variáveis de decisão
    4. Restrições (básicas e condicionais)
    5. Função objetivo (custo de geração, emissão, déficit)

    Todas as dependências são resolvidas na ordem correta para evitar conflitos e omissões.

    Args:
        model (ConcreteModel): Modelo Pyomo.
        system (FullSystem): Objeto com os dados do sistema elétrico.
    """
    definir_conjuntos(model, system)
    definir_parametros(model, system)
    definir_variaveis(model)
    definir_restricoes(model, system)
    definir_objetivo(model)
