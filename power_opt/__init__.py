"""
Pacote `power_opt`

Este é o pacote principal do projeto de despacho ótimo de energia elétrica.

Agrupa todos os módulos e subpacotes necessários para:
- Definição dos modelos de otimização
- Implementação dos solucionadores com diferentes abordagens (Pyomo, Scipy)
- Manipulação de dados de entrada e saída
- Geração de gráficos e relatórios
- Análises de viabilidade, perdas e déficit

Subpacotes:
- `models`: definição dos elementos do sistema elétrico
- `solver`: solucionadores e lógica de otimização
- `utils`: utilitários para conversão, carregamento e limpeza de dados

Autor: Giovani Santiago Junqueira
"""

__author__ = "Giovani Santiago Junqueira"

# Importações iniciais para facilitar acesso de alto nível
from . import models
from . import solver
from . import utils
