"""
:module: flags
:summary: Pacote de controle condicional de lógica por flags.
:author: Giovani Santiago Junqueira

Este pacote agrupa funções que implementam lógicas condicionais no modelo
de otimização, ativadas por flags configuradas no sistema.

Inclui:
- Restrições de rampa
- Modelagem de déficit
- Termos de emissão de CO₂
- Transporte de energia (balanço de potência)
- Fluxo de potência DC
- Iterações de cálculo e redistribuição de perdas elétricas
"""

__author__ = "Giovani Santiago Junqueira"

from .utils import flag_ativa, safe_del
from .emissao import aplicar_emissao
from .deficit import aplicar_deficit
from .rampa import aplicar_rampa
from .transporte import aplicar_transporte
from .fluxo_dc import aplicar_fluxo_dc
from .perdas import (aplicar_perdas_iterativamente)
__all__ = [
    "aplicar_emissao",
    "aplicar_deficit",
    "aplicar_rampa",
    "aplicar_transporte",
    "aplicar_fluxo_dc",
    "aplicar_perdas_iterativamente",
    "flag_ativa",
    "safe_del"
]
