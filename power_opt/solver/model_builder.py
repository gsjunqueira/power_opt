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
    Constraint, NonNegativeReals, Objective, Param, Reals,
    Set, Var, minimize, Suffix)
from power_opt.solver.flags import (
    aplicar_deficit, aplicar_emissao, aplicar_transporte, aplicar_rampa)


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

    if system.config.get("usar_deficit", False):

        model.D = Set(initialize=[(d.bus, d.period) for d in system.deficits], dimen=2)

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

    if system.config.get("considerar_emissao", False):
        model.emissao = Param(model.G,
            initialize={g.id: g.emission for bus in system.buses.values() for g in bus.generators}
        )
        model.custo_emissao = Param(initialize=system.config["custo_emissao"])

    if system.config.get("considerar_rampa", False):
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

    if system.config.get("usar_deficit", False) and hasattr(model, "D"):
        model.cost_deficit = Param(
            model.B, model.T,
            initialize={(d.bus, d.period): d.cost for d in system.deficits},
            within=NonNegativeReals,
            default=0.0
        )

        model.max_deficit = Param(
            model.D,
            initialize={(d.bus, d.period): d.max_deficit for d in system.deficits},
            within=NonNegativeReals,
            default=0.0
        )

    if system.config.get("considerar_fluxo", False):
        model.susceptance = Param(model.L,
            initialize={linha.id: linha.susceptance for linha in system.lines},
            within=Reals
        )
        model.conductance = Param(model.L,
            initialize={linha.id: linha.conductance for linha in system.lines},
            within=Reals
        )

        model.f_max = Param(
            model.L,
            initialize={linha.id: linha.limit for linha in system.lines},
            within=NonNegativeReals
        )

def definir_variaveis(model, system):
    """
    Define as variáveis de decisão do modelo.

    Args:
        model (ConcreteModel): Modelo Pyomo.
        system (FullSystem): Objeto que contém os dados do sistema elétrico.
    """
    safe_del(model, 'F')
    safe_del(model, 'Deficit')
    safe_del(model, 'dual')
    safe_del(model, 'P')

    model.P = Var(model.G, model.T, domain=NonNegativeReals)

    if system.deficits:
        model.Deficit = Var(model.D, domain=NonNegativeReals)

    if system.config.get("considerar_fluxo", False):
        model.F = Var(model.L, model.T, domain=Reals)

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

    # Aplica lógica condicional de fluxo (transporte) se configurada
    aplicar_transporte(model, system)

    # Aplica lógica condicional de rampas se configurada
    aplicar_rampa(model, system)

    # Parte associada ao déficit ou geradores fictícios
    aplicar_deficit(model, system)


def definir_objetivo(model, system):
    """
    Define a função objetivo do modelo de otimização.

    A função objetivo pondera o custo de geração, a penalidade por emissão e o custo do déficit.

    Args:
        model (ConcreteModel): Modelo Pyomo.
        system (FullSystem): Objeto que contém os dados do sistema elétrico.
    """
    # Parte do custo total e da penalidade por emissão
    aplicar_emissao(model, system)



    def f_obj(model): # pylint: disable=unused-argument
        """FOB = Custo total de geração + penalidade por emissão + custo do déficit"""
        return model.fob_emissao.expr + model.custo_deficit.expr

    model.objetivo = Objective(rule=f_obj, sense=minimize)

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
    definir_variaveis(model, system)
    definir_restricoes(model, system)
    definir_objetivo(model, system)

def safe_del(model, attr):
    """
    Remove com segurança um componente do modelo Pyomo, caso ele exista.

    Esta função é utilizada para evitar conflitos ao redefinir variáveis, parâmetros
    ou restrições em reconstruções iterativas do modelo. Se o atributo estiver presente
    no modelo, ele será removido explicitamente com `del_component()`.

    Args:
    -----
    model : ConcreteModel
        Instância do modelo Pyomo onde o componente pode existir.

    attr : str
        Nome do atributo a ser removido do modelo (ex: 'F', 'P', 'dual').
    """
    if hasattr(model, attr):
        model.del_component(getattr(model, attr))
