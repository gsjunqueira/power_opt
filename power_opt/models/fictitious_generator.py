"""
Defines a special generator for balancing system mismatches.

Autor: Giovani Santiago Junqueira
"""

# pylint: disable=too-few-public-methods


from .base_generator import BaseGenerator

class FictitiousGenerator(BaseGenerator):
    """
    Generator used only to ensure feasibility by absorbing or supplying excess power.

    Attributes:
        ramp (float): Large ramp for flexibility.
        cost (float): High cost to discourage usage.
        emission (float): Zero by default.
    """

    def __init__(self, bus: str, id_: str = None, max_flow: float = 1e5, cost: float = 1e6):
        if id_ is None:
            id_ = f"GF{bus}"
        super().__init__(id_, bus, -max_flow, max_flow, type_="fictitious", fictitious=True)
        self.ramp = max_flow
        self.cost = cost
        self.emission = 0.0


    def get_power_output(self, period: int) -> float:
        return self.pg  # ou 0.0, se mais adequado
