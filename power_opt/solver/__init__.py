"""
Pacote `solver` responsável por conter os modelos de otimização utilizados no projeto.

Este pacote oferece duas abordagens:
- `PyomoSolver`: implementação baseada no framework Pyomo.
- `ScipySolver`: implementação baseada em scipy.optimize.linprog.

Ambas as classes expõem métodos para construção e solução do problema de despacho ótimo.

Autor: Giovani Santiago Junqueira
"""

from .modelo_pyomo import PyomoSolver

__all__ = ["PyomoSolver"]
