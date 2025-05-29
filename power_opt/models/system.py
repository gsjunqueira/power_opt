"""
Módulo que define a classe Sistema para consolidar os componentes elétricos
e organizar os dados necessários à resolução do fluxo de potência ou despacho otimizado.

A classe Sistema encapsula a topologia e os dados elétricos do sistema, incluindo:
- Lista de barras, linhas, transformadores e geradores
- Perfil de carga por período
- Cascata de usinas hidrelétricas (se aplicável)
- Parâmetros de base (potência base) e configuração
- Perdas estimadas por barra e período (inicialmente zero)

Essa abordagem promove modularidade, clareza e facilidade de extensão,
facilitando o uso em modelos lineares iterativos ou simulações.

Autor: Giovani Santiago Junqueira
"""

# pylint: disable=line-too-long

from collections import defaultdict
from typing import Dict, List, Optional, Tuple
from power_opt.models import Bus, Line, Load, Deficit

class System:
    """
    Representa o sistema elétrico completo, incluindo barras, linhas, cargas e parâmetros auxiliares.

    A classe é responsável por armazenar toda a estrutura da rede elétrica e os dados
    operacionais utilizados durante a otimização.

    Attributes:
        buses (Dict[str, Bus]): Dicionário de objetos de barra indexados por ID.
        lines (List[Line]): Lista de linhas de transmissão.
        load_profile (List[List[Load]]): Lista de cargas por período.
        base_power (float): Valor da potência base do sistema (MVA).
        config (dict): Dicionário de configurações gerais.
        cascata (Optional[dict]): Estrutura de cascata para usinas hidrelétricas.
        perdas_barras (Dict[str, Dict[int, float]]): Perdas por barra e por período em PU.
    """

    def __init__(self):
        """Inicializa o objeto System com estruturas vazias e valores padrão."""
        self.buses: Dict[str, Bus] = {}
        self.lines: List[Line] = []
        self.load_profile: List[List[Load]] = []
        self.deficits: List[Deficit] = []
        self.base_power: float = 100.0
        self.config: dict = {}
        self.cascata: Optional[dict] = None
        self.perdas_barras: Dict[str, Dict[int, float]] = defaultdict(lambda: defaultdict(float))
        self.line_dict = {line.id: line for line in self.lines}
        self.deficit_map: Dict[Tuple[str, int], Deficit] = {
            (d.bus, d.period): d for d in self.deficits
        }

    def add_bus(self, bus: Bus):
        """Adiciona uma barra ao sistema.

        Args:
            bus (Bus): Objeto de barra a ser adicionado.
        """
        self.buses[bus.id] = bus

    def add_line(self, line: Line):
        """Adiciona uma linha de transmissão ao sistema.

        Args:
            line (Line): Objeto de linha a ser adicionado.
        """
        self.lines.append(line)

    def get_bus(self, bus_id: str) -> Bus:
        """Recupera uma barra a partir de seu identificador.

        Args:
            bus_id (str): Identificador da barra.

        Returns:
            Bus: Objeto da barra correspondente.
        """
        return self.buses[bus_id]

    def update_line_dict(self):
        """Update the dictionary for fast access to lines by their ID."""
        self.line_dict = {line.id: line for line in self.lines}

    def get_line(self, from_bus: str, to_bus: str) -> Line:
        """Retorna a linha de transmissão que conecta duas barras.

        Args:
            from_bus (str): Barra de origem.
            to_bus (str): Barra de destino.

        Returns:
            Line: Objeto da linha correspondente.

        Raises:
            ValueError: Se a linha não for encontrada.
        """
        for line in self.lines:
            if line.from_bus == from_bus and line.to_bus == to_bus:
                return line
        raise ValueError(f"Linha de {from_bus} para {to_bus} não encontrada.")

    def set_cascata(self, cascata: dict):
        """Define a estrutura de cascata das usinas hidrelétricas.

        Args:
            cascata (dict): Dicionário com as relações de dependência entre usinas.
        """
        self.cascata = cascata

    def get_jusante(self, id_: str) -> str | None:
        """
        Gets the downstream plant of a given hydro plant.

        Args:
            id_ (str): ID of the hydro plant.

        Returns:
            str or None: ID of the downstream hydro plant, if any.
        """
        for item in self.cascata:
            if item["id"] == id_:
                return item.get("jusante")
        return None

    def resumo(self):
        """
        Exibe um resumo informativo do sistema carregado.

        Este método imprime no console um resumo textual contendo:
        - A base de potência adotada (em MVA);
        - O número total de barras do sistema;
        - O número de linhas de transmissão;
        - O número de períodos considerados no perfil de carga;
        - O número total de cargas em todos os períodos;
        - O número total de geradores, discriminando quantos são reais e quantos são fictícios;
        - O número de relações de cascata cadastradas (se houver).

        Essa função é útil para verificar rapidamente se os dados do sistema foram carregados corretamente.
        """
        print("📦 RESUMO DO SISTEMA CARREGADO")
        print(f"- Base de potência: {self.base_power} MVA")
        print(f"- N. de barras: {len(self.buses)}")
        print(f"- N. de linhas: {len(self.lines)}")
        print(f"- N. de períodos: {len(self.load_profile)}")
        print(f"- N. de cargas totais: {sum(len(p) for p in self.load_profile)}")

        total_geradores = sum(len(b.generators) for b in self.buses.values())
        ficticios = sum(g.fictitious for b in self.buses.values() for g in b.generators)
        reais = total_geradores - ficticios

        print(f"- N. de geradores totais: {total_geradores} (Reais: {reais}, Fictícios: {ficticios})")
        print(f"- N. de relações de cascata: {len(self.cascata) if self.cascata else 0}")
        print("")

    def get_deficit(self, bus: str, period: int) -> Optional[Deficit]:
        """
        Retorna o objeto Deficit associado a uma barra e período específicos, se existir.

        Esta função consulta o mapeamento interno `deficit_map` que associa tuplas
        (bus, period) a objetos Deficit, permitindo acesso rápido ao corte de carga
        permitido para cada barra no horizonte de planejamento.

        Args:
            bus (str): Identificador da barra onde o déficit pode ocorrer.
            period (int): Índice temporal (período) do planejamento.

        Returns:
            Optional[Deficit]: O objeto Deficit correspondente, ou None se não houver
            déficit definido para a combinação de barra e período informada.
        """
        return self.deficit_map.get((bus, period))
