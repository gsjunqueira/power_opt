"""
Deficit model representing curtailed load (corte de carga) with penalized cost.

Autor: Giovani Santiago Junqueira
"""

from dataclasses import dataclass

@dataclass
class Deficit:
    """
    Represents a load deficit (load shedding) at a given bus and time period.

    Attributes:
        id (str): Unique identifier of the deficit variable.
        bus (str): Bus to which the deficit is associated.
        period (int): Time index for the deficit.
        max_deficit (float): Upper bound for allowed load shedding [pu].
        cost (float): Penalty cost per unit of deficit [$ / pu].
    """
    id: str
    bus: str
    period: int
    max_deficit: float
    cost: float = 1e6
