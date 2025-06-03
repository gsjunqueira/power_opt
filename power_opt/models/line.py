"""
Módulo `line`

Define a classe `Line`, que representa uma linha de transmissão entre duas barras no
sistema elétrico. Contém atributos elétricos como condutância, susceptância e capacidade
máxima de transporte, essenciais para o cálculo de perdas e fluxo de potência.

Autor: Giovani Santiago Junqueira
"""

__author__ = "Giovani Santiago Junqueira"

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
