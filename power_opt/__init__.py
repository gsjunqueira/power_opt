"""
Pacote `power_opt`

Este pacote contém os módulos principais para otimização de despacho de sistemas elétricos,
incluindo modelos matemáticos, solucionadores e utilitários auxiliares.

Estrutura:
- models/: Definição das entidades do sistema (barras, geradores, linhas etc.)
- solver/: Implementação dos algoritmos de otimização (Pyomo, Scipy, etc.)
- utils/: Funções auxiliares para leitura, exportação e análise dos resultados

Autor: Giovani Santiago Junqueira
"""

# Importações iniciais para facilitar acesso de alto nível
from . import models
from . import solver
from . import utils
