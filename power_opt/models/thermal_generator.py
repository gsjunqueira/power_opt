"""
Thermal generator with cost, emission, and ramp constraints.

Autor: Giovani Santiago Junqueira
"""

# pylint: disable=too-few-public-methods, too-many-arguments, too-many-positional-arguments

from .base_generator import BaseGenerator

class ThermalGenerator(BaseGenerator):
    """
    Represents a thermal generator.

    Attributes:
        ramp (float): Ramp limit [MW/h].
        cost (float): Generation cost [R$/MWh].
        emission (float): Emission rate [tCO₂/MWh].
    """

    def __init__(self, id_: str, bus: str, gmin: float, gmax: float,
                 ramp: float, cost: float, emission: float, fictitious: bool = False):
        super().__init__(id_, bus, gmin, gmax, type_="thermal", fictitious=fictitious)
        self.ramp = ramp
        self.cost = cost
        self.emission = emission

    def get_power_output(self, period: int) -> float:
        return self.pg  # ou implemente lógica específica, se necessário
