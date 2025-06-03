"""
Pacote `solver`

Contém os solucionadores e construtores de modelos para despacho ótimo de energia
elétrica. Atualmente, utiliza Pyomo como principal framework de otimização.

Módulos:
- pyomo_solver: classe principal de resolução usando Pyomo.
- model_builder: funções modulares para construção do modelo Pyomo.

Subpacotes:
- `flags`: contém os módulos responsáveis por ativar funcionalidades específicas no modelo de
otimização do despacho de energia elétrica. Cada módulo implementa lógica condicional associada
a uma flag:
- `handler`: Contém módulos auxiliares para gerenciamento de configuração, extração de resultados,
depuração, visualização e exportação de saídas do modelo de otimização.


Autor: Giovani Santiago Junqueira
"""

__author__ = "Giovani Santiago Junqueira"

# from .modelo_pyomo import PyomoSolver
from .model_builder import build_model
from .pyomo_solver import PyomoSolver
from . import flags
from . import handler

__all__ = [ "PyomoSolver", "build_model", "flags", "handler"]
