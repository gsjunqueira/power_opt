"""
Pacote `solver`

Este pacote fornece solucionadores para o problema de despacho ótimo de energia elétrica,
permitindo a simulação de diferentes abordagens matemáticas.

Abordagens disponíveis:
- PyomoSolver: baseia-se na biblioteca Pyomo para modelagem e resolução.

Cada solucionador implementa uma interface consistente para montagem, execução e análise
de modelos de otimização.

Autor: Giovani Santiago Junqueira
"""

__author__ = "Giovani Santiago Junqueira"

from .bus import Bus
from .load import Load
from .line import Line
from .deficit import Deficit
from .system import System
from .base_generator import BaseGenerator
from .thermal_generator import ThermalGenerator
from .fictitious_generator import FictitiousGenerator
from .hydro_generator import HydroGenerator
from .wind_generator import WindGenerator



__all__ = ["Bus", "Load", "Line", "System", "BaseGenerator", "ThermalGenerator",
           "FictitiousGenerator", "HydroGenerator", "WindGenerator", "Deficit"]
