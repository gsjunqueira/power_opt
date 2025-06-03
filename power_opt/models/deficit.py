"""
Módulo `deficit`

Responsável por adicionar a variável de corte de carga (déficit) ao modelo de otimização,
bem como suas respectivas restrições e penalidades no custo total.

Essa modelagem permite capturar a insuficiência de geração em cenários onde a demanda
não pode ser totalmente atendida.

Autor: Giovani Santiago Junqueira
"""

__author__ = "Giovani Santiago Junqueira"

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
