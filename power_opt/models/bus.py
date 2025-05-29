"""
Defines the Bus class that represents a node in the power system.

Each bus may be connected to one or more generators and loads.

Autor: Giovani Santiago Junqueira
"""

from typing import List
from .load import Load
from .base_generator import BaseGenerator


class Bus:
    """
    Represents a bus in the power system.

    Attributes:
        id (str): Unique bus identifier.
        generators (list[BaseGenerator]): List of generators connected to the bus.
        loads (list[Load]): List of loads connected to the bus.
    """

    def __init__(self, id_: str):
        self.id: str = id_
        self.generators: List[BaseGenerator] = []
        self.loads: List[Load] = []

    def add_generator(self, generator: BaseGenerator):
        """
        Adds a generator to the bus.

        Args:
            generator (BaseGenerator): Generator instance to attach.
        """
        self.generators.append(generator)

    def add_load(self, load: Load):
        """
        Adds a load to the bus.

        Args:
            load (Load): Load instance to attach.
        """
        self.loads.append(load)
