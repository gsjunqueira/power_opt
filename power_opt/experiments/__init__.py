"""
Pacote `experimentos`

Este pacote contém os módulos responsáveis pela execução sistemática de simulações de
otimização aplicadas a sistemas elétricos, permitindo estudos de sensibilidade, variação
de parâmetros (e.g., delta), testes de configurações com e sem perdas, uso de fluxo DC,
penalidades por emissão e modelagem de déficit.

Objetivo:
- Automatizar campanhas de simulação.
- Isolar a lógica de experimentação do `main.py`.
- Permitir reuso e reprodutibilidade dos estudos realizados.

Este pacote é particularmente útil em análises de planejamento energético, onde se deseja
avaliar diferentes configurações de operação sob cenários controlados.

Autor: Giovani Santiago Junqueira
"""

__author__ = "Giovani Santiago Junqueira"

from .experimentos import simular_delta, simular_n_menos_1

__all__ = ["simular_delta", "simular_n_menos_1"]
