"""
Módulo que define o modelo de despacho otimizado utilizando o Pyomo.

Permite simular diferentes configurações do sistema elétrico com base em flags:
- considerar_fluxo: ativa a modelagem do fluxo de potência entre barras
- considerar_perdas: ativa o cálculo de perdas por linha
- considerar_emissao: inclui penalidade por emissão de CO2 na função objetivo
- considerar_rampa: aplica restrição de rampa nos geradores

O modelo pode ser resolvido com diferentes solvers compatíveis com Pyomo.

Autor: Giovani Santiago Junqueira
"""

# pylint: disable=line-too-long, too-many-arguments, too-many-instance-attributes, too-many-locals, too-many-positional-arguments, invalid-name

import csv
from pyomo.environ import (
    inequality, ConcreteModel, Var, Objective, Constraint, SolverFactory,
    NonNegativeReals, Reals, minimize, value, Set, Param, RangeSet, Any
)


class PyomoSolver:
    """
    Classe que encapsula o modelo de otimização de despacho utilizando Pyomo.

    A construção do modelo depende de flags que controlam se fluxo, perdas,
    rampa e emissão devem ser considerados.
    """

    def __init__(self, system, considerar_fluxo=True, considerar_perdas=True,
                 considerar_emissao=True, considerar_rampa=True):
        """
        Inicializa a classe com as configurações escolhidas.

        Args:
            system (System): Objeto do sistema elétrico com topologia e dados.
            considerar_fluxo (bool): Se deve modelar os fluxos nas linhas.
            considerar_perdas (bool): Se deve calcular perdas por linha.
            considerar_emissao (bool): Se deve incluir penalidade de emissão na FOB.
            considerar_rampa (bool): Se deve aplicar restrição de rampa entre períodos.
        """
        self.system = system
        self.model = ConcreteModel()
        self.resultado = None

        self.modo_debug = False  # Ativa logs detalhados para depuração
        self.debug_csv_path = None # Caminho do arquivo CSV de debug (se desejado)
        self.iteracao_atual = 0
        self.considerar_fluxo = considerar_fluxo
        self.considerar_perdas = considerar_perdas if considerar_fluxo else False
        self.considerar_emissao = considerar_emissao
        self.considerar_rampa = considerar_rampa
        self.perdas_computadas = False
        self._resolvendo_perdas = False
        self._perdas_resultado = {}
        self._carga_base = {
            t: sum(c.demand for c in cargas)
            for t, cargas in enumerate(self.system.load_profile)
        }

    def construir(self):
        """Executa a construção completa do modelo com base nas flags definidas."""
        self._definir_indices()
        self._definir_variaveis_geracao()
        if self.considerar_fluxo:
            self._definir_variaveis_fluxo()

        self._definir_parametros_geradores()
        self._definir_parametros_carga()
        if self.considerar_fluxo:
            self._definir_parametros_linhas()
        self._definir_parametros_configuracao()

        self._definir_restricoes_geracao()
        if self.considerar_fluxo:
            self._definir_restricoes_fluxo()

        if self.considerar_rampa:
            self._definir_restricoes_rampa()

        self._definir_restricoes_barras()
        self._definir_objetivo()

    def _definir_indices(self):
        """Define os conjuntos principais: geradores, barras, tempos e linhas (se habilitado)."""
        model = self.model
        model.G = Set(initialize=[g.id for b in self.system.buses.values() for g in b.generators])
        model.B = Set(initialize=list(self.system.buses.keys()))
        model.T = RangeSet(0, len(self.system.load_profile) - 1)
        model.L = Set(initialize=[l.id for l in self.system.lines])
        model.F = Var(model.L, model.T, domain=Reals)

    def _definir_variaveis_geracao(self):
        """Cria variável de geração para cada gerador e período."""
        self.model.P = Var(self.model.G, self.model.T, within=NonNegativeReals)

    # def _definir_variaveis_fluxo(self):
    #     """Cria variável de fluxo de potência entre barras para cada período."""
    #     self.model.F = Var(self.model.L, self.model.T, domain=Reals)

    def _definir_variaveis_fluxo(self):
        """Cria variável de fluxo de potência entre barras para cada período."""
        if hasattr(self.model, "F"):
            self.model.del_component("F")
        self.model.F = Var(self.model.L, self.model.T, domain=Reals)

    def _definir_parametros_geradores(self):
        """Inicializa parâmetros dos geradores: custo, emissão, rampa, gmin, gmax."""
        model = self.model
        sistema = self.system
        custo = {}
        emissao = {}
        rampa = {}
        gmin = {}
        gmax = {}

        for b in sistema.buses.values():
            for g in b.generators:
                custo[g.id] = g.cost
                emissao[g.id] = g.emission
                rampa[g.id] = g.ramp
                gmin[g.id] = g.gmin
                gmax[g.id] = g.gmax

        model.custo = Param(model.G, initialize=custo)
        model.emissao = Param(model.G, initialize=emissao)
        model.rampa = Param(model.G, initialize=rampa)
        model.gmin = Param(model.G, initialize=gmin)
        model.gmax = Param(model.G, initialize=gmax)

    def _definir_parametros_carga(self):
        """Carrega a demanda por barra e tempo a partir do perfil de carga do sistema."""
        model = self.model
        sistema = self.system
        demanda = {(load.bus, t): load.demand for t, cargas in enumerate(sistema.load_profile) for load in cargas}
        model.demanda = Param(model.B, model.T, initialize=demanda, default=0)

    def _definir_parametros_linhas(self):
        """
        Inicializa os parâmetros das linhas:
        - susceptância
        - condutância
        - limite de fluxo (em pu)
        - barra de origem
        - barra de destino

        Essa definição só é feita se o fluxo for considerado.
        """
        if not self.considerar_fluxo:
            return  # Ignora definição se o fluxo não é considerado

        model = self.model
        sistema = self.system

        susceptancia = {}
        condutancia = {}
        limite = {}
        origem = {}
        destino = {}

        for linha in sistema.lines:
            chave = linha.id
            susceptancia[chave] = linha.susceptance
            condutancia[chave] = linha.conductance
            limite[chave] = linha.limit
            origem[chave] = linha.from_bus
            destino[chave] = linha.to_bus

        model.susceptance = Param(model.L, initialize=susceptancia)
        model.conductance = Param(model.L, initialize=condutancia)
        model.line_limit = Param(model.L, initialize=limite, mutable=True)
        model.origin = Param(model.L, initialize=origem, within=Any)
        model.destination = Param(model.L, initialize=destino, within=Any)

    def _definir_parametros_configuracao(self):
        """Define os parâmetros globais da configuração do sistema."""
        cfg = self.system.config
        self.model.base = Param(initialize=self.system.base_power)
        self.model.delta = Param(initialize=cfg.get("delta", 0.0))
        self.model.custo_emissao = Param(initialize=cfg.get("custo_emissao", 0.0))

    def _definir_restricoes_geracao(self):
        """Aplica limites mínimo e máximo de geração para cada gerador."""
        model = self.model

        def limites(model, g, t):
            """Restrição de geração: mantém P dentro dos limites gmin e gmax."""
            return inequality(model.gmin[g], model.P[g, t], model.gmax[g])

        model.limites = Constraint(model.G, model.T, rule=limites)

    def _definir_restricoes_fluxo(self):
        """Aplica limites de fluxo máximo nas linhas."""

        if not self.considerar_fluxo:
            return  # Ignora definição das restrições de fluxo

        model = self.model

        def limites_fluxo(model, l, t):
            """Restrição de fluxo: mantém F entre -limite e +limite da linha."""
            return inequality(-model.line_limit[l], model.F[l, t], model.line_limit[l])

        model.limites_fluxo = Constraint(model.L, model.T, rule=limites_fluxo)

    def _definir_restricoes_rampa(self):
        """Aplica restrição de rampa de subida e descida entre períodos consecutivos."""
        model = self.model

        def rampa_subida(model, g, t):
            """Limita a variação positiva da geração entre períodos consecutivos."""
            if t == 0:
                return Constraint.Skip
            return model.P[g, t] - model.P[g, t - 1] <= model.rampa[g]

        def rampa_descida(model, g, t):
            """Limita a variação negativa da geração entre períodos consecutivos."""
            if t == 0:
                return Constraint.Skip
            return model.P[g, t - 1] - model.P[g, t] <= model.rampa[g]

        model.rampa_sup = Constraint(model.G, model.T, rule=rampa_subida)
        model.rampa_inf = Constraint(model.G, model.T, rule=rampa_descida)

    def _definir_restricoes_barras(self):
        """Aplica o balanço de potência em cada barra e período, considerando ou não perdas e fluxos."""
        model = self.model
        sistema = self.system

        if self.considerar_fluxo:
            def balanco(model, b, t):
                """Aplica o balanço de potência na barra b no tempo t."""
                geradores_na_barra = [g.id for g in sistema.buses[b].generators]
                geracao = sum(model.P[g, t] for g in geradores_na_barra)
                carga = model.demanda[b, t] if (b, t) in model.demanda else 0
                entrada = sum(model.F[l, t] for l in model.L if model.destination[l] == b)
                saida = sum(model.F[l, t] for l in model.L if model.origin[l] == b)
                return geracao + entrada - saida == carga
            model.balanco = Constraint(model.B, model.T, rule=balanco)
        else:
            def balanco_total(model, t):
                """Balanço total do sistema: soma gerações = soma cargas"""
                total_geracao = sum(model.P[g, t] for g in model.G)
                total_carga = sum(model.demanda[b, t] for b in model.B)
                return total_geracao - total_carga == 0

            model.balanco = Constraint(model.T, rule=balanco_total)

    def _definir_objetivo(self):
        """Define a função objetivo ponderada entre custo de geração e penalidade por emissão."""
        model = self.model

        def f_obj(model):
            """Minimiza a função objetivo ponderando custo e penalidade de emissão."""
            custo_total = sum(model.P[g, t] * model.custo[g] for g in model.G for t in model.T)
            penal_emissao = sum(model.P[g, t] * model.emissao[g] for g in model.G for t in model.T)
            return model.delta * custo_total + (1 - model.delta) * model.custo_emissao * penal_emissao

        model.objetivo = Objective(rule=f_obj, sense=minimize)

    def _aplicar_perdas_e_reconstruir(self, solver_name, tee):
        """
        Executa o cálculo iterativo de perdas nas linhas, redistribuindo essas perdas como cargas fictícias por barra,
        sem sobrescrever a carga real original. Reconstrói e resolve o modelo até convergência.

        Args:
            solver_name (str): Nome do solver a ser utilizado (por exemplo, 'glpk').
            tee (bool): Exibe ou não a saída detalhada do solver.
        """
        self._resolvendo_perdas = True
        self.iteracao_atual = 0  # Controla o número da iteração de perdas
        max_iter, epsilon = 40, 1e-16
        iteracao, convergiu = 0, False

        carga_base = self._armazenar_carga_base()
        perdas_anterior = self._inicializar_perdas()

        while not convergiu and iteracao < max_iter:
            self._resolver_modelo(solver_name, tee)
            perdas_atual, perda_total = self._calcular_perdas_linha()
            self._atualizar_cargas_com_perdas(carga_base, perdas_atual)

            diff_per_barra = self._calcular_diferenca_perda(perdas_anterior, perdas_atual)
            self._imprimir_iteracao(iteracao, perda_total, diff_per_barra, carga_base, perdas_atual)

            if diff_per_barra < epsilon:
                convergiu = True
            else:
                perdas_anterior = perdas_atual.copy()
                self.model = ConcreteModel()
                self.construir()
            iteracao += 1
            self.iteracao_atual += 1

        if not convergiu:
            raise RuntimeError("❌ O processo de redistribuição de perdas não convergiu.")

        self.considerar_perdas = False
        self.perdas_computadas = True
        self.model = ConcreteModel()
        self.construir()
        self._resolver_modelo(solver_name, tee)
        self._resolvendo_perdas = False

    def _armazenar_carga_base(self):
        """
        Armazena a carga original de cada barra e tempo antes da introdução das perdas.

        Returns:
            dict: Dicionário com chaves (bus, t) e valores de demanda originais.
        """
        return {
            (load.bus, t): load.demand
            for t, cargas in enumerate(self.system.load_profile)
            for load in cargas
        }

    def _inicializar_perdas(self):
        """
        Inicializa o dicionário de perdas por barra e tempo com valores zero.

        Returns:
            dict: Dicionário (bus, t) → 0.0
        """
        return {
            (bus, t): 0.0
            for bus in self.system.buses
            for t in range(len(self.system.load_profile))
        }

    def _resolver_modelo(self, solver_name, tee):
        """
        Resolve o modelo de otimização utilizando o solver especificado.

        Args:
            solver_name (str): Nome do solver a ser utilizado (por exemplo, 'glpk').
            tee (bool): Exibe ou não a saída detalhada do solver.
        """
        solver = SolverFactory(solver_name)
        solver.solve(self.model, tee=tee)

    def _calcular_perdas_linha(self):
        """
        Calcula as perdas por linha para cada período de tempo com base no fluxo e na condutância.

        Returns:
            tuple: 
                - dict: Perdas por barra e tempo (bus, t) → MW.
                - float: Perda total acumulada no sistema.
        """
        model = self.model
        perdas = self._inicializar_perdas()
        perda_total = 0.0

        for l in self.system.lines:
            G = value(model.conductance[l.id])
            B = value(model.susceptance[l.id])
            for t in list(model.T):
                f = value(model.F[l.id, t])
                theta = f / B if B != 0 else 0.0
                perda = G * (theta ** 2)
                perda_total += perda
                perdas[(l.from_bus, t)] += 0.5 * perda
                perdas[(l.to_bus, t)] += 0.5 * perda

                # 🔍 Chamada para depuração detalhada, se ativada
                self._debug_perda_linha(l.id, t, f, B, theta, G, perda, iteracao=self.iteracao_atual)

        return perdas, perda_total

    def _atualizar_cargas_com_perdas(self, carga_base, perdas):
        """
        Atualiza a demanda total em cada barra/tempo, somando a perda à carga base.

        Args:
            carga_base (dict): Carga original (bus, t) → MW.
            perdas (dict): Perda calculada (bus, t) → MW.
        """
        for t, cargas in enumerate(self.system.load_profile):
            for carga in cargas:
                chave = (carga.bus, t)
                carga.demand = carga_base[chave] + perdas[chave]


    def _calcular_diferenca_perda(self, perdas_ant, perdas_nova):
        """
        Compara o valor de perdas entre duas iterações.

        Args:
            perdas_ant (dict): Perdas anteriores.
            perdas_nova (dict): Perdas atuais.

        Returns:
            float: Soma absoluta das diferenças de perdas.
        """
        return sum(abs(perdas_nova[k] - perdas_ant[k]) for k in perdas_ant)


    def _imprimir_iteracao(self, iteracao, perda_total, diff, carga_base, perdas):
        """
        Imprime informações detalhadas de cada iteração: perda total e carga com perda por barra e tempo.

        Args:
            iteracao (int): Número da iteração atual.
            perda_total (float): Perda total do sistema na iteração.
            diff (float): Diferença agregada de perdas por barra entre iterações.
            carga_base (dict): Carga original.
            perdas (dict): Perdas atuais.
        """
        print(f"📦 Iteração {iteracao} - Perda total = {perda_total:.6f}, Δ_per_barra = {diff:.6e}")
        for b in self.system.buses:
            for t in range(len(self.system.load_profile)):
                chave = (b, t)
                total = carga_base[chave] + perdas[chave]
                print(f"  Barra {b}, t={t} → demanda = {total:.6f}, perda = {perdas[chave]:.6f}")

    def solve(self, solver_name="highs", tee=False):
        """Resolve o modelo usando o solver especificado."""

        # Prevenção de recursão ao aplicar perdas
        if getattr(self, "_resolvendo_perdas", False):
            return

        solver = SolverFactory(solver_name)
        self.resultado = solver.solve(self.model, tee=tee)

        # Se for para considerar perdas, ajustar demanda e reconstruir o modelo
        if self.considerar_perdas:
            self._resolvendo_perdas = True
            try:
                self._aplicar_perdas_e_reconstruir(solver_name, tee)
            finally:
                self._resolvendo_perdas = False

        # 🔍 Debug pós-solução
        self._debug_geracao()
        self._debug_objetivo()
        self._debug_balanco_barras()

    def mostrar_resultados(self):
        """Imprime o resultado da otimização."""
        model = self.model
        sistema = self.system

        print("+--------------------------+")
        fob = value(model.objetivo)
        print(f"\nFOB (Função Objetivo): $ {fob:.2f}")

        print("\nGeração por gerador:")
        for g in model.G:
            for t in list(model.T):
                p = value(model.P[g, t]) * sistema.base_power
                print(f"  {g} [t={t}] = {p:.2f} MW")

        # Fluxo de potência nas linhas
        print("\nFluxo de potência nas linhas:")
        if self.considerar_fluxo:
            for l in model.L:
                for t in list(model.T):
                    fluxo = value(model.F[l, t]) * sistema.base_power
                    print(f"  Linha ({l}) [t={t}] = {fluxo:.2f} MW")

        # Perdas nas linhas
        if self.perdas_computadas and self._perdas_resultado:
            print("\nPerdas de potência nas linhas:")
            for l in model.L:
                for t in list(model.T):
                    chave = f"{l}_{t}"
                    perda = self._perdas_resultado.get(chave, 0.0)
                    print(f"  Perda ({l}) [t={t}] = {perda:.2f} MW")

    def mostrar_balanco(self):
        """Imprime o balanço de potência total por período."""
        model = self.model
        sistema = self.system

        print("\n📊 Balanço por período (MW):")
        for t in list(model.T):
            geracao = sum(value(model.P[g, t]) for g in model.G) * sistema.base_power
            carga_original = self._carga_base[t] * sistema.base_power
            perdas = 0.0
            if self.perdas_computadas and self._perdas_resultado:
                perdas = sum(
                    self._perdas_resultado.get(f"{l}_{t}", 0.0)
                    for l in model.L
                )

            print(f"  t={t}: Geração={geracao:.2f} | Carga={carga_original:.2f}"
                + (f" | Perdas={perdas:.2f}" if self.perdas_computadas else "")
                + f" → Δ={(geracao - carga_original - perdas):+.4f} MW")

    def get_result(self) -> dict:
        """
        Retorna um dicionário com os principais resultados da otimização para análise e comparação.

        Inclui:
        - Parâmetros do cenário (delta, flags de restrições)
        - FOB (função objetivo)
        - Geração total (MW)
        - Perdas totais (MW) se computadas
        - Fluxo por linha e período
        - Geração por gerador e período

        Args:
            delta (float, opcional): Valor do parâmetro delta, se aplicável ao experimento.

        Returns:
            dict: Dicionário com os resultados e parâmetros da execução.
        """
        model = self.model
        base = self.system.base_power
        resultado = {
            "delta": value(self.model.delta),
            "FOB": value(model.objetivo),
            "perdas_MW": sum(self._perdas_resultado.values()),
            "geracao_MW": sum(
                value(model.P[g, t]) for g in model.G for t in list(model.T)
            ) * base,
            "considerar_fluxo": self.considerar_fluxo,
            "considerar_perdas": self.perdas_computadas,
            "considerar_rampa": self.considerar_rampa,
            "considerar_emissao": self.considerar_emissao,
        }

        for l in model.L:
            for t in list(model.T):
                resultado[f"fluxo_{l}_{t}"] = value(model.F[l, t]) * base

        for g in model.G:
            for t in list(model.T):
                resultado[f"ger_{g}_{t}"] = value(model.P[g, t]) * base

        return resultado

    def _debug_perda_linha(self, linha_id, t, f, B, theta, G, perda, iteracao=None):
        """
        Exibe e (opcionalmente) salva os detalhes do cálculo de perda por linha.

        Args:
            linha_id (str): ID da linha.
            t (int): Período de tempo.
            f (float): Fluxo da linha (pu).
            B (float): Susceptância da linha.
            theta (float): Diferença angular estimada.
            G (float): Condutância da linha.
            perda (float): Perda de potência (MW).
        """
        if not self.modo_debug:
            return

        msg = f"[DEBUG] Linha {linha_id} | t={t} | f={f:.6f} pu | B={B:.6f} | θ={theta:.6f} rad | G={G:.6f} → perda = {perda:.6f} MW"
        print(msg)

        if self.debug_csv_path:
            # Acrescenta 'iteracao' no início, se fornecido
            cabecalho = ["iteracao", "linha", "tempo", "f", "B", "theta", "G", "perda"] if iteracao is not None \
                else ["linha", "tempo", "f", "B", "theta", "G", "perda"]
            linha = [iteracao, linha_id, t, f, B, theta, G, perda] if iteracao is not None \
                else [linha_id, t, f, B, theta, G, perda]

            # Cria o arquivo e escreve cabeçalho se ainda não existir
            try:
                with open(self.debug_csv_path, "x", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow(cabecalho)
                    writer.writerow(linha)
            except FileExistsError:
                with open(self.debug_csv_path, "a", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow(linha)

    def _debug_geracao(self):
        """
        Exibe os valores de geração por gerador e tempo, se o modo debug estiver ativado.
        """
        if not self.modo_debug:
            return
        print("\n[DEBUG] Geração por gerador:")
        for g in self.model.G:
            for t in list(self.model.T):
                p = value(self.model.P[g, t]) * self.system.base_power
                print(f"  {g} [t={t}] = {p:.4f} MW")

    def _debug_objetivo(self):
        """
        Exibe a decomposição da função objetivo em custo e emissão, se o modo debug estiver ativado.
        """
        if not self.modo_debug:
            return
        model = self.model
        # base = self.system.base_power
        custo_total = sum(value(model.P[g, t]) * model.custo[g] for g in model.G for t in model.T)
        emissao_total = sum(value(model.P[g, t]) * model.emissao[g] for g in model.G for t in list(model.T))
        fob = value(model.objetivo)
        print("\n[DEBUG] Decomposição da FOB:")
        print(f"  Custo total: {custo_total:.2f}")
        print(f"  Emissão total: {emissao_total:.2f}")
        print(f"  FOB total: {fob:.2f}")
        print(f"  Delta: {value(model.delta):.2f} | Peso emissão: {(1 - value(model.delta)):.2f} | Custo emissão: {value(model.custo_emissao):.2f}")

    def _debug_balanco_barras(self):
        """
        Exibe o balanço de potência em cada barra e tempo, se o modo debug estiver ativado.
        """
        if not self.modo_debug:
            return
        print("\n[DEBUG] Balanço de potência por barra:")
        model = self.model
        sistema = self.system

        for b in model.B:
            for t in list(model.T):
                geradores_na_barra = [g.id for g in sistema.buses[b].generators]
                geracao = sum(value(model.P[g, t]) for g in geradores_na_barra)
                carga = value(model.demanda[b, t])
                entrada = sum(value(model.F[l, t]) for l in model.L if value(model.destination[l]) == b) if self.considerar_fluxo else 0.0
                saida = sum(value(model.F[l, t]) for l in model.L if value(model.origin[l]) == b) if self.considerar_fluxo else 0.0
                delta = geracao + entrada - saida - carga
                print(f"  Barra {b} [t={t}] → Geração = {geracao:.4f}, Carga = {carga:.4f}, Entrada = {entrada:.4f}, Saída = {saida:.4f}, Δ = {delta:+.6f}")
