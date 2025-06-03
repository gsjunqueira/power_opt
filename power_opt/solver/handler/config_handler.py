"""
Módulo `config_handler`

Responsável por definir, validar e manipular os parâmetros de configuração
utilizados na construção do modelo de otimização.

Autor: Giovani Santiago Junqueira
"""

__author__ = "Giovani Santiago Junqueira"

def extrair_configuracoes(system):
    """
    Extrai as configurações do dicionário do sistema e retorna como flags booleanas.
    """
    config = system.config
    return {
        "usar_deficit": config.get("usar_deficit", False),
        "considerar_fluxo": config.get("considerar_fluxo", False),
        "considerar_perdas": config.get("considerar_perdas", False),
        "considerar_rampa": config.get("considerar_rampa", False),
        "considerar_emissao": config.get("considerar_emissao", False),
    }

def aplicar_configuracoes(pyomo_solver, config_dict):
    """
    Aplica um dicionário de configurações ao solver PyomoSolver.
    """
    pyomo_solver.usar_deficit = config_dict["usar_deficit"]
    pyomo_solver.considerar_fluxo = config_dict["considerar_fluxo"]
    pyomo_solver.considerar_perdas = config_dict["considerar_perdas"]
    pyomo_solver.considerar_rampa = config_dict["considerar_rampa"]
    pyomo_solver.considerar_emissao = config_dict["considerar_emissao"]
