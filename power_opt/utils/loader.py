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
from power_opt.models import (
    Bus, Load, Line, System,
    ThermalGenerator, HydroGenerator, WindGenerator, FictitiousGenerator
)


def extrair_numero_id(raw_id: str) -> str:
    """
    Extrai a parte numérica (ou útil) do ID para gerar identificadores consistentes.
    Exemplo: 'G1' → '1', 'E23' → '23', 'H01' → '01'
    """
    match = re.search(r"\d.*", raw_id)
    return match.group() if match else raw_id


class DataLoader:
    """
    Loads a power system definition from a JSON file and builds the corresponding System object.
    """

    def __init__(self, json_path: str):
        """
        Initializes the loader with the given JSON path.

        Args:
            json_path (str): Path to the structured JSON file.
        """
        self.path = Path(json_path)
        if not self.path.exists():
            raise FileNotFoundError(f"JSON file not found: {self.path}")

    def load_system(self) -> System:
        """
        Reads the JSON file and returns a populated System object.

        Returns:
            System: The fully constructed power system.
        """
        with open(self.path, "r", encoding="utf-8") as f:
            data = json.load(f)

        system = System()
        system.base_power = data.get("PB", 100.0)
        system.config = data.get("config", {})

        # Criar barras
        for bus_data in data.get("barras", []):
            bus = Bus(id_=bus_data["id"])
            system.add_bus(bus)

        # Criar geradores com prefixo automático
        has_hydro = False
        for gen_data in data.get("geradores", []):
            tipo = gen_data.get("tipo", "thermal").lower()
            num_id = extrair_numero_id(gen_data["id"])

            if tipo == "thermal":
                id_ = f"GT{num_id}"
                gen = ThermalGenerator(
                    id_=id_,
                    bus=gen_data["barra"],
                    gmin=gen_data["gmin"] / system.base_power,
                    gmax=gen_data["gmax"] / system.base_power,
                    ramp=gen_data["rampa"] / system.base_power,
                    cost=gen_data["custo"] * system.base_power,
                    emission=gen_data["emissao"] * system.base_power,
                    fictitious=gen_data.get("ficticio", False)
                )

            elif tipo == "hydro":
                id_ = f"GH{num_id}"
                gen = HydroGenerator(
                    id_=id_,
                    bus=gen_data["barra"],
                    gmin=gen_data["gmin"] / system.base_power,
                    gmax=gen_data["gmax"] / system.base_power,
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
                    gmin=gen_data["gmin"] / system.base_power,
                    gmax=gen_data["gmax"] / system.base_power,
                    power_curve=gen_data["curva_potencia"],
                    fictitious=gen_data.get("ficticio", False)
                )

            else:
                raise ValueError(f"Tipo de gerador desconhecido: {tipo}")

            system.get_bus(gen.bus).add_generator(gen)

        # Criar linhas
        for i, line_data in enumerate(data.get("linhas", [])):
            line = Line(
                line_id=f"L{i}",
                from_bus=line_data["de"],
                to_bus=line_data["para"],
                limit=line_data["limite"] / system.base_power,
                susceptance=line_data["susceptancia"] / system.base_power,
                conductance=line_data["condutancia"] / system.base_power
            )
            system.add_line(line)

        # Perfil de carga temporal
        for t, cargas in enumerate(data.get("carga", [])):
            periodo = []
            for carga_data in cargas:
                carga = Load(
                    id_=carga_data["id"],
                    bus=carga_data["barra"],
                    demand=carga_data["demanda"] / system.base_power,
                    period=t
                )
                periodo.append(carga)
            system.load_profile.append(periodo)

        # Geradores fictícios com prefixo GF
        barras_com_carga = set(
            carga.bus for periodo in system.load_profile for carga in periodo
        )

        for bus_id in barras_com_carga:
            id_ = f"GF{extrair_numero_id(bus_id)}"
            fict = FictitiousGenerator(bus=bus_id, id_=id_)
            system.get_bus(bus_id).add_generator(fict)
            print(f"⚠️  Fictitious generator added at bus {bus_id} with id {id_}")

        # Cascata (apenas se houver hidrelétricas)
        if has_hydro and "cascata" in data:
            system.set_cascata(data["cascata"])
            print(f"ℹ️  Cascata hidráulica carregada com {len(data['cascata'])} relações.")


        system.update_line_dict()

        # Garante que todas as barras tenham ao menos uma carga em todos os períodos
        for t, cargas in enumerate(system.load_profile):
            for bus in system.buses.values():
                if not any(c.bus == bus.id for c in cargas):
                    cargas.append(Load(id_=f"CF_{bus.id}_t{t}", bus=bus.id, demand=0.0, period=t))

        return system
