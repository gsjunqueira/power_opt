"""
Módulo `pyomo_solver`

Executa o modelo de despacho de geração utilizando o framework Pyomo.

Este módulo é o ponto de entrada para simulações baseadas em otimização,
integrando as seguintes etapas:
- Construção modular do modelo via `model_builder`.
- Aplicação de configurações.
- Execução iterativa com cálculo de perdas (se ativado).
- Extração de resultados, duais e informações de depuração.

Dependências:
- config_handler.py
- model_builder.py
- result_handler.py
- debug_handler.py
- dual_handler.py

Autor: Giovani Santiago Junqueira
"""

__author__ = "Giovani Santiago Junqueira"

# pylint: disable=invalid-name, line-too-long

from pyomo.environ import ConcreteModel

from power_opt.solver.handler import (extrair_configuracoes,
    aplicar_configuracoes, extrair_resultados, extrair_duais_em_dataframe, extrair_debug
    )
from power_opt.solver.flags import (aplicar_perdas_iterativamente)
from power_opt.solver import build_model


class PyomoSolver:
    """
    Classe que encapsula a execução do modelo de otimização via Pyomo.
    """

    def __init__(self, system):
        """
        Inicializa o PyomoSolver com o sistema fornecido.

        Parâmetros:
        ----------
        system : FullSystem
            Objeto que contém os dados do sistema a ser modelado.
        """
        self.system = system
        self.model = ConcreteModel()
        self._resolvendo_perdas = False
        self.config_flags = None
        self.model_built = False
        self._perdas_finais = None

    def set_resolvendo_perdas(self, flag: bool):
        """
        Define o status interno de resolução iterativa com perdas.
        """
        self._resolvendo_perdas = flag

    def set_perdas_finais(self, perdas: dict):
        """
        Armazena o dicionário de perdas finais após convergência.
        """
        self._perdas_finais = perdas

    def build(self, **kwargs):
        """
        Constrói o modelo a partir do sistema e aplica as configurações fornecidas.

        Parâmetros:
        ----------
        kwargs : dict
            Dicionário com flags de configuração para o modelo.
        """
        self.config_flags = kwargs
        build_model(self.model, self.system)

        config_dict = extrair_configuracoes(self.system)
        aplicar_configuracoes(self, config_dict)

        self.model_built = True

    def solve(self, solver_name="highs", tee=False):
        """
        Resolve o modelo com o solver especificado, com ou sem iteração de perdas.

        Parâmetros:
        ----------
        solver_name : str, default="highs"
            Nome do solver a ser utilizado (e.g., "glpk", "highs").
        tee : bool, default=False
            Se True, imprime informações detalhadas da solução.
        """

        aplicar_perdas_iterativamente(self, solver_name=solver_name, tee=tee)

    def get_results(self) -> dict:
        """
        Extrai os resultados da otimização.

        Retorna:
        -------
        dict
            Dicionário com os resultados principais da execução.
        """
        return extrair_resultados(self.model, self.system)

    def get_duals(self) -> dict:
        """
        Extrai as variáveis duais (multiplicadores de Lagrange) do modelo.

        Retorna:
        -------
        dict
            Dicionário com as variáveis duais por restrição.
        """
        return extrair_duais_em_dataframe(self.model)

    def get_debug(self, linha_id, t, f, B, theta, G, perda, considerar_fluxo,
                  modo_debug=True) -> dict:
        """
        Encaminha para a função get_debug do debug_handler.

        Parâmetros:
        -----------
        linha_id : str
        t : int
        f : float
        B : float
        theta : float
        G : float
        perda : float
        considerar_fluxo : bool
        modo_debug : bool

        Retorna:
        --------
        dict: Resultado de depuração.
        """
        return extrair_debug(
            model=self.model,
            system=self.system,
            linha_id=linha_id,
            t=t,
            f=f,
            B=B,
            theta=theta,
            G=G,
            perda=perda,
            considerar_fluxo=considerar_fluxo,
            modo_debug=modo_debug
        )
