"""
Módulo `config_handler`

Este módulo centraliza a lógica de extração e aplicação das configurações
(`config`) utilizadas no modelo de otimização.

Ele oferece funções auxiliares para:
- Extrair os parâmetros de configuração armazenados no objeto `system`.
- Aplicar esses parâmetros como atributos do solver (por exemplo, PyomoSolver).

Isso facilita a manutenção, evita duplicação de código e permite alterar
futuramente a origem das configurações (por exemplo, de JSON para interface gráfica)
sem impacto nas demais partes do código.

Funções:
    - extrair_configuracoes(system): Retorna um dicionário de flags extraídas do sistema.
    - aplicar_configuracoes(pyomo_solver, config_dict): Aplica essas configurações no solver.

Autor: Giovani Santiago Junqueira
"""

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
