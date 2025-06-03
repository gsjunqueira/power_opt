"""
Módulo `fictitious_generator`

Define a classe `FictitiousGenerator`, que representa um gerador fictício utilizado para
balancear o sistema em situações de déficit de geração. Estes geradores são adicionados
automaticamente às barras com carga e permitem viabilizar soluções inviáveis.

Autor: Giovani Santiago Junqueira
"""

__author__ = "Giovani Santiago Junqueira"

# pylint: disable=too-few-public-methods, too-many-arguments, too-many-positional-arguments

from .base_generator import BaseGenerator

class WindGenerator(BaseGenerator):
    """
    Represents a wind generator with power curve parameters.

    Attributes:
        power_curve (dict): Power output in MW as a function of wind speed.
    """

    def __init__(self, id_: str, bus: str, gmin: float, gmax: float,
                 power_curve: dict, fictitious: bool = False):
        super().__init__(id_, bus, gmin, gmax, type_="wind", fictitious=fictitious)
        self.power_curve = power_curve  # Dictionary mapping wind speed to power output

    def get_power_output(self, period: int) -> float:
        return self.pg  # ou implemente lógica específica, se necessário
