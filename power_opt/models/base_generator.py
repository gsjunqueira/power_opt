from abc import ABC, abstractmethod
from typing import Optional

class BaseGenerator(ABC):
    def __init__(self, id: str, bus, gmin: float = 0.0, gmax: float = 0.0,
                 qmin: Optional[float] = None, qmax: Optional[float] = None,
                 type_: str = "generic", fictitious: bool = False, status: bool = True):
        self.id = id
        self.bus = bus
        self.gmin = gmin
        self.gmax = gmax
        self.qmin = qmin
        self.qmax = qmax
        self.pg = 0.0
        self.qg = 0.0
        self.type = type_
        self.fictitious = fictitious
        self.status = status

    @abstractmethod
    def get_power_output(self, period: int) -> float:
        pass