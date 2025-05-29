"""
Module that defines the Line class, representing a transmission line in the power system.

Each line connects two buses and includes electrical parameters such as
susceptance and conductance, as well as thermal flow limits.

Autor: Giovani Santiago Junqueira
"""

# pylint: disable=too-few-public-methods, too-many-arguments, too-many-positional-arguments

class Line:
    """
    Represents a transmission line with electrical and operational characteristics.

    Attributes:
        id (str): ID of the line
        from_bus (str): ID of the sending bus.
        to_bus (str): ID of the receiving bus.
        limit (float): Power flow capacity limit (MW).
        susceptance (float): Susceptance (B, in pu or appropriate unit).
        conductance (float): Conductance (G, in pu or appropriate unit).
    """

    def __init__(self, line_id: str, from_bus: str, to_bus: str, limit: float,
                 susceptance: float, conductance: float):
        self.id = line_id
        self.from_bus = from_bus
        self.to_bus = to_bus
        self.limit = limit
        self.susceptance = susceptance
        self.conductance = conductance
