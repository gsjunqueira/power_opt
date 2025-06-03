"""
Módulo `perdas`

Implementa a lógica para cálculo iterativo de perdas nas linhas de transmissão.

As perdas são calculadas com base no fluxo e condutância das linhas, e redistribuídas
como carga adicional nas barras extremas. O processo é repetido até convergência.

Autor: Giovani Santiago Junqueira
"""

__author__ = "Giovani Santiago Junqueira"

from typing import Dict, Tuple
from pyomo.environ import value


def inicializar_perdas(system) -> Dict[Tuple[str, int], float]:
    """
    Inicializa o dicionário de perdas por barra e tempo com valores zero.

    Args:
        system: Objeto do sistema com as barras.

    Returns:
        dict: Mapa (barra, tempo) → 0.0
    """
    return {
        (bus, t): 0.0
        for bus in system.buses
        for t in range(len(system.load_profile))
    }


def armazenar_carga_base(system) -> Dict[Tuple[str, int], float]:
    """
    Armazena a carga original de cada barra e tempo antes da introdução das perdas.

    Args:
        system: Objeto do sistema com as cargas.

    Returns:
        dict: (barra, t) → carga original
    """
    return {
        (load.bus, t): load.demand
        for t, cargas in enumerate(system.load_profile)
        for load in cargas
    }


def calcular_perdas(model, system) -> Tuple[Dict[Tuple[str, int], float], float]:
    """
    Calcula as perdas por linha e redistribui como carga em cada barra.

    Args:
        model: Modelo Pyomo já resolvido.
        system: Objeto do sistema contendo linhas.
        iteracao (int): Número da iteração para depuração (opcional).

    Returns:
        Tuple:
            - perdas_por_barra: dict (bus, t) → MW de perda
            - perda_total: float com perda total acumulada
    """
    perdas = inicializar_perdas(system)
    perda_total = 0.0

    for linha in system.lines:
        condutancia = value(model.conductance[linha.id])
        susceptancia = value(model.susceptance[linha.id])

        for t in list(model.T):
            fluxo = value(model.F[linha.id, t])
            theta = fluxo / susceptancia if susceptancia != 0 else 0.0
            perda = condutancia * (theta ** 2)
            perda_total += perda

            perdas[(linha.from_bus, t)] += 0.5 * perda
            perdas[(linha.to_bus, t)] += 0.5 * perda

    return perdas, perda_total


def atualizar_cargas_com_perdas(system, carga_base: Dict[Tuple[str, int], float],
                                perdas: Dict[Tuple[str, int], float]) -> None:
    """
    Atualiza a carga total de cada barra somando a perda equivalente.

    Args:
        system: Objeto do sistema com perfil de carga.
        carga_base: Carga original (bus, t) → MW
        perdas: Perda redistribuída (bus, t) → MW
    """
    for t, cargas in enumerate(system.load_profile):
        for carga in cargas:
            chave = (carga.bus, t)
            carga.demand = carga_base[chave] + perdas[chave]


def calcular_diferenca_perdas(p1: Dict[Tuple[str, int], float],
                              p2: Dict[Tuple[str, int], float]) -> float:
    """
    Compara perdas entre duas iterações.

    Args:
        p1: Perdas anteriores
        p2: Perdas atuais

    Returns:
        Soma absoluta das diferenças
    """
    return sum(abs(p2[k] - p1[k]) for k in p1)
