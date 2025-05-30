"""
DataLoader module to construct a System object from a structured JSON file.

Supports multiple generator types (thermal, hydro, wind), time-dependent loads,
transmission losses, and optional cascade topology. Generator IDs are automatically
prefixed by type for identification (e.g., GT, GH, GW, GF).

Autor: Giovani Santiago Junqueira
"""

import json
import re
from pathlib import Path
from typing import Optional
from collections import defaultdict
from power_opt.models import (
    Bus, Load, Line, System, Deficit,
    ThermalGenerator, HydroGenerator, WindGenerator, FictitiousGenerator
)


def extrair_numero_id(raw_id: str) -> str:
    """
    Extrai a parte numérica (ou útil) do ID para gerar identificadores consistentes.
    Exemplo: 'G1' → '1', 'E23' → '23', 'H01' → '01'

    Args:
        raw_id (str): Identificador bruto.

    Returns:
        str: Parte numérica extraída do ID.
    """
    match = re.search(r"\d.*", raw_id)
    return match.group() if match else raw_id


class DataLoader:
    """
    Classe responsável por carregar os dados de um sistema elétrico a partir de um arquivo JSON
    estruturado e construir um objeto System correspondente.
    """

    def __init__(self, json_path: str):
        """
        Inicializa o carregador com o caminho para o arquivo JSON.

        Args:
            json_path (str): Caminho para o arquivo JSON estruturado.
        """
        self.path = Path(json_path)
        if not self.path.exists():
            raise FileNotFoundError(f"JSON file not found: {self.path}")
        self.system: Optional[System] = None
        self.has_hydro: bool = False

    def load_system(self) -> System:
        """
        Lê o arquivo JSON e retorna um objeto System populado com os dados.

        Returns:
            System: Objeto do sistema elétrico completo.
        """
        with open(self.path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.system = System()
        self.system.base_power = data.get("PB", 100.0)
        self.system.config = data.get("config", {})

        self.system.config["usar_deficit"] = self.system.config.get("usar_deficit", False)

        self._carregar_barras(data)
        self._carregar_geradores(data)
        self._carregar_linhas(data)
        self._carregar_cargas(data)
        if self.system.config.get("usar_deficit", False):
            self._carregar_deficits(data)
        else:
            self._adicionar_geradores_ficticios()
        self._carregar_cascata(data)
        self.system.update_line_dict()
        self._garantir_carga_minima()

        return self.system

    def _carregar_barras(self, data):
        """
        Carrega e adiciona as barras (buses) ao sistema.

        Args:
            data (dict): Dados extraídos do JSON.
        """
        for bus_data in data.get("barras", []):
            bus = Bus(id_=bus_data["id"])
            self.system.add_bus(bus)

    def _carregar_geradores(self, data):
        """
        Carrega os geradores térmicos, hidráulicos e eólicos e os associa às barras.

        Args:
            data (dict): Dados extraídos do JSON.
        """
        has_hydro = False
        for gen_data in data.get("geradores", []):
            tipo = gen_data.get("tipo", "thermal").lower()
            num_id = extrair_numero_id(gen_data["id"])

            if tipo == "thermal":
                id_ = f"GT{num_id}"
                gen = ThermalGenerator(
                    id_=id_,
                    bus=gen_data["barra"],
                    gmin=gen_data["gmin"] / self.system.base_power,
                    gmax=gen_data["gmax"] / self.system.base_power,
                    ramp=gen_data["rampa"] / self.system.base_power,
                    cost=gen_data["custo"] * self.system.base_power,
                    emission=gen_data["emissao"] * self.system.base_power,
                    fictitious=gen_data.get("ficticio", False)
                )

            elif tipo == "hydro":
                id_ = f"GH{num_id}"
                gen = HydroGenerator(
                    id_=id_,
                    bus=gen_data["barra"],
                    gmin=gen_data["gmin"] / self.system.base_power,
                    gmax=gen_data["gmax"] / self.system.base_power,
                    volume_min=gen_data["volume_min"],
                    volume_max=gen_data["volume_max"],
                    productivity=gen_data["produtividade"],
                    fictitious=gen_data.get("ficticio", False)
                )
                has_hydro = True

            elif tipo == "wind":
                id_ = f"GW{num_id}"
                gen = WindGenerator(
                    id_=id_,
                    bus=gen_data["barra"],
                    gmin=gen_data["gmin"] / self.system.base_power,
                    gmax=gen_data["gmax"] / self.system.base_power,
                    power_curve=gen_data["curva_potencia"],
                    fictitious=gen_data.get("ficticio", False)
                )
            else:
                raise ValueError(f"Tipo de gerador desconhecido: {tipo}")

            self.system.get_bus(gen.bus).add_generator(gen)

        self.has_hydro = has_hydro

    def _carregar_linhas(self, data):
        """
        Carrega as linhas de transmissão e as adiciona ao sistema.

        Args:
            data (dict): Dados extraídos do JSON.
        """
        for i, line_data in enumerate(data.get("linhas", [])):
            line = Line(
                line_id=f"L{i}",
                from_bus=line_data["de"],
                to_bus=line_data["para"],
                limit=line_data["limite"] / self.system.base_power,
                susceptance=line_data["susceptancia"] / self.system.base_power,
                conductance=line_data["condutancia"] / self.system.base_power
            )
            self.system.add_line(line)

    def _carregar_cargas(self, data):
        """
        Carrega o perfil de carga ao longo do tempo.

        Args:
            data (dict): Dados extraídos do JSON.
        """
        for t, cargas in enumerate(data.get("carga", [])):
            periodo = []
            for carga_data in cargas:
                carga = Load(
                    id_=carga_data["id"],
                    bus=carga_data["barra"],
                    demand=carga_data["demanda"] / self.system.base_power,
                    period=t
                )
                periodo.append(carga)
            self.system.load_profile.append(periodo)

    def _adicionar_geradores_ficticios(self):
        """
        Adiciona geradores fictícios (com ID GF) em todas as barras que possuem carga.
        """
        barras_com_carga = set(
            carga.bus for periodo in self.system.load_profile for carga in periodo
        )
        for bus_id in barras_com_carga:
            id_ = f"GF{extrair_numero_id(bus_id)}"
            fict = FictitiousGenerator(bus=bus_id, id_=id_)
            self.system.get_bus(bus_id).add_generator(fict)
            print(f"⚠️  Fictitious generator added at bus {bus_id} with id {id_}")

    def _carregar_deficits(self, data):
        """
        Carrega os déficits a partir do JSON (se presentes) ou os gera
        automaticamente com base na carga.

        Args:
            data (dict): Dados extraídos do JSON.
        """
        if "deficits" in data:
            for d in data["deficits"]:
                id_ = f"CUT_{d['bus']}_t{d['period']}"
                deficit = Deficit(
                    id=id_,
                    bus=d["bus"],
                    period=d["period"],
                    max_deficit=d["limite"],
                    cost=d["custo"]
                )
                self.system.deficits.append(deficit)
            print(f"ℹ️  {len(self.system.deficits)} déficits carregados diretamente do JSON.")
        else:
            demanda_por_barra_tempo = defaultdict(float)
            for t, cargas in enumerate(self.system.load_profile):
                for carga in cargas:
                    demanda_por_barra_tempo[(carga.bus, t)] += carga.demand

            for (bus, t), demanda_total in demanda_por_barra_tempo.items():
                id_ = f"CUT_{bus}_t{t}"
                deficit = Deficit(
                    id=id_,
                    bus=bus,
                    period=t,
                    max_deficit=demanda_total,
                    cost=10000.0
                )
                self.system.deficits.append(deficit)
            print(f"⚠️  Déficits não definidos no JSON — {len(self.system.deficits
                  )} gerados automaticamente com custo fixo.")

    def _carregar_cascata(self, data):
        """
        Carrega a estrutura de cascata hidráulica, se houver hidrelétricas presentes.

        Args:
            data (dict): Dados extraídos do JSON.
        """
        if self.has_hydro and "cascata" in data:
            self.system.set_cascata(data["cascata"])
            print(f"ℹ️  Cascata hidráulica carregada com {len(data['cascata'])} relações.")

    def _garantir_carga_minima(self):
        """
        Garante que todas as barras tenham pelo menos uma carga (mesmo que zero) em cada período.
        """
        for t, cargas in enumerate(self.system.load_profile):
            for bus in self.system.buses.values():
                if not any(c.bus == bus.id for c in cargas):
                    cargas.append(Load(id_=f"CF_{bus.id}_t{t}", bus=bus.id, demand=0.0, period=t))
