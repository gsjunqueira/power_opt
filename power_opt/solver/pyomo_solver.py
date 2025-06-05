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

import os
from pyomo.environ import ConcreteModel, Suffix
from pyomo.opt import SolverFactory

from power_opt.solver.handler import (extrair_configuracoes,
    aplicar_configuracoes, extrair_resultados, extrair_duais_em_dataframe, extrair_debug
    )
from power_opt.solver.flags import (inicializar_perdas, armazenar_carga_base, calcular_perdas,
                     atualizar_cargas_com_perdas, calcular_diferenca_perdas)
from power_opt.solver import build_model, safe_del


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
        # self.model.pprint()

        # Extrai o dicionário de configurações do sistema
        config_dict = extrair_configuracoes(self.system)

        # Aplica corretamente as configurações ao solver (self)
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

        # print("🧩 Entrando no solve()")
        # print(f"Model já construído? {self.model_built}")

        if self.config_flags.get("considerar_perdas", False):
            self.aplicar_perdas_iterativamente(solver_name=solver_name, tee=tee)
        else:
            if solver_name == 'glpk':
                safe_del(self.model, 'dual')
                self.model.dual = Suffix(direction=Suffix.IMPORT)
                os.environ["PATH"] = "/opt/homebrew/bin:" + os.environ["PATH"]
                solver = SolverFactory(solver_name, executable="/opt/homebrew/bin/glpsol")
            else:                                                                                                                                                                                                                       
                solver = SolverFactory(solver_name)

            solver.solve(self.model, tee=tee)

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

    def aplicar_perdas_iterativamente(self, solver_name="highs", tee=False, max_iter=40, epsilon=1e-16):
        """
        Executa o processo iterativo de cálculo e redistribuição de perdas por linha no sistema.

        A cada iteração, o modelo é resolvido, as perdas são calculadas e redistribuídas como carga.
        O processo continua até convergência ou atingir o número máximo de iterações.

        Parâmetros:
        -----------
        solver_name : str
            Nome do solver a ser utilizado (default = 'highs').

        tee : bool
            Se True, exibe o log do solver.

        max_iter : int
            Número máximo de iterações permitidas.

        epsilon : float
            Critério de convergência baseado na diferença absoluta entre perdas sucessivas.
        """
        self._resolvendo_perdas = True
        iteracao = 0
        convergiu = False

        carga_base = armazenar_carga_base(self.system)
        perdas_ant = inicializar_perdas(self.system)

        while not convergiu and iteracao < max_iter:
            # Resolve o modelo com configuração atual

            if solver_name.lower() == 'glpk':
                safe_del(self.model, 'dual')
                self.model.dual = Suffix(direction=Suffix.IMPORT)
                os.environ["PATH"] = "/opt/homebrew/bin:" + os.environ["PATH"]
                solver = SolverFactory(solver_name, executable="/opt/homebrew/bin/glpsol")
            else:
                solver = SolverFactory(solver_name)
            solver.solve(self.model, tee=tee)

            # Calcula perdas e redistribui como carga
            print(f'iteracao atual = {iteracao}')
            perdas_atuais, perda_total = calcular_perdas(self.model, self.system)
            atualizar_cargas_com_perdas(self.system, carga_base, perdas_atuais)

            # Verifica convergência
            delta = calcular_diferenca_perdas(perdas_ant, perdas_atuais)
            # print(f"📦 Iteração {iteracao} - Perda total = {perda_total:.6f}, Δ_per_barra = {delta:.6e}")

            if delta < epsilon:
                convergiu = True
                self._perdas_finais = {
                    "perda_linha": perdas_atuais,
                    "perda_total": perda_total,
                }

            else:
                perdas_ant = perdas_atuais.copy()
                self.model = ConcreteModel()
                if solver_name.lower() == 'glpk':
                    safe_del(self.model, 'dual')
                    self.model.dual = Suffix(direction=Suffix.IMPORT)
                self.build(**self.config_flags)

            iteracao += 1

        if not convergiu:
            raise RuntimeError(
                "❌ O processo de perdas não convergiu após o número máximo de iterações.")

        # Etapa final: resolver uma última vez com modelo já convergido
        self.model = ConcreteModel()
        if solver_name.lower() == 'glpk':
            safe_del(self.model, 'dual')
            self.model.dual = Suffix(direction=Suffix.IMPORT)
        self.model_built = False
        self.build(**self.config_flags)
        if solver_name == 'glpk':
            os.environ["PATH"] = "/opt/homebrew/bin:" + os.environ["PATH"]
            solver = SolverFactory(solver_name, executable="/opt/homebrew/bin/glpsol")
        else:
            solver = SolverFactory(solver_name)
        solver.solve(self.model, tee=tee)

        self._resolvendo_perdas = False
