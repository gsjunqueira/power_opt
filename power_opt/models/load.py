"""
Módulo `load`

Define a classe `Load`, que representa uma carga elétrica conectada a uma barra. Permite
a modelagem de diferentes níveis de demanda ao longo do horizonte de simulação.

Autor: Giovani Santiago Junqueira
"""

__author__ = "Giovani Santiago Junqueira"

# pylint: disable=too-few-public-methods

class Load:
    """
    Represents a load connected to a bus at a specific time period.

    Attributes:
        id (str): Identifier of the load.
        bus (str): ID of the associated bus.
        demand (float): Load demand in MW.
        period (int): Time period index (e.g., hour).
    """
    def __init__(self, id_: str, bus: str, demand: float, period: int):
        self.id = id_
        self.bus = bus
        self.demand = demand
        self.period = period
