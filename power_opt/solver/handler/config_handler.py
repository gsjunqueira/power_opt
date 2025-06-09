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
        "deficit": config.get("deficit", False),
        "transporte": config.get("transporte", False),
        "fluxo_dc": config.get("fluxo_dc", False),
        "perdas": config.get("perdas", False),
        "rampa": config.get("rampa", False),
        "emissao": config.get("emissao", False),
    }

def aplicar_configuracoes(pyomo_solver, config_dict):
    """
    Aplica um dicionário de configurações ao solver PyomoSolver.
    """
    pyomo_solver.deficit = config_dict["deficit"]
    pyomo_solver.transporte = config_dict["transporte"]
    pyomo_solver.fluxo_dc = config_dict["fluxo_dc"]
    pyomo_solver.perdas = config_dict["perdas"]
    pyomo_solver.rampa = config_dict["rampa"]
    pyomo_solver.emissao = config_dict["emissao"]
