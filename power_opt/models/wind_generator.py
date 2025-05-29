"""
Defines a wind generator with a power curve.
"""

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
