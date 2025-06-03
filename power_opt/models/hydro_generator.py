"""
Módulo `hydro_generator`

Implementa a classe `HydroGenerator`, uma especialização de `BaseGenerator` voltada para
geradores hidrelétricos. Permite a futura integração de restrições de volume, afluência,
rampa hidráulica e produção de energia associada.

Autor: Giovani Santiago Junqueira
"""

__author__ = "Giovani Santiago Junqueira"

# pylint: disable=too-few-public-methods, too-many-arguments, too-many-positional-arguments

from .base_generator import BaseGenerator

class HydroGenerator(BaseGenerator):
    """
    Represents a hydroelectric generator.

    Attributes:
        volume_min (float): Minimum reservoir volume (MW).
        volume_max (float): Maximum reservoir volume (MW).
        productivity (float): Energy produced per unit of water (MW).
    """

    def __init__(self, id_: str, bus: str, gmin: float, gmax: float,
                 volume_min: float, volume_max: float, productivity: float,
                 fictitious: bool = False):
        super().__init__(id_, bus, gmin, gmax, type_="hydro", fictitious=fictitious)
        self.volume_min = volume_min
        self.volume_max = volume_max
        self.productivity = productivity

    def get_power_output(self, period: int) -> float:
        return self.pg  # ou implemente lógica específica, se necessário
