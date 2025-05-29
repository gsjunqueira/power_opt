"""
Manual testing script for the DataLoader and system structure.

This script is used during development to validate the structure
of the loaded power system, including time-dependent load profiles
and fictitious generators.
"""

# pylint: disable=line-too-long

from power_opt.utils import DataLoader


def show_system_summary(system):
    """
    Prints a detailed summary of the system's structure.
    """
    print("\n📊 Power System Overview")
    print(f"  ▪ Base power: {system.base_power:.1f} MVA")
    print(f"  ▪ Time periods: {len(system.load_profile)}")
    print(f"  ▪ Buses: {len(system.buses)}")
    print(f"  ▪ Lines: {len(system.lines)}")

    total_gens = 0
    total_fict = 0
    for bus in system.buses.values():
        total_gens += len(bus.generators)
        total_fict += sum(g.fictitious for g in bus.generators)
    print(f"  ▪ Generators: {total_gens} (fictitious: {total_fict})")


def show_loads_by_period(system):
    """
    Prints the load profile for each time period.
    """
    print("\n🕒 Load profile by period:")
    for t, cargas in enumerate(system.load_profile):
        print(f"  ▪ Period {t}:")
        for carga in cargas:
            print(f"     ▪ Load {carga.id} at bus {carga.bus} = {carga.demand:.2f} MW")


def show_generators(system):
    """
    Prints a summary of all generators.
    """
    print("\n⚡ Generator overview:")
    for bus in system.buses.values():
        for gen in bus.generators:
            tipo = "fictitious" if gen.fictitious else "real"
            print(f"  ▪ {gen.id} ({tipo}) at {gen.bus} — "
                  f"{gen.gmin:.1f}-{gen.gmax:.1f} MW | ramp: {gen.ramp} MW/h | "
                  f"cost: {gen.cost} | emission: {gen.emission}")


def show_lines(system):
    """
    Prints all transmission lines.
    """
    print("\n🔌 Transmission lines:")
    for line in system.lines:
        print(f"  ▪ {line.from_bus} → {line.to_bus} | limit: {line.limit} MW | B: {line.susceptance}, G: {line.conductance}")

if __name__ == "__main__":
    JSON_PATH = "data/dados_base.json"
    loader = DataLoader(JSON_PATH)
    sistema = loader.load_system()

    show_system_summary(sistema)
    show_loads_by_period(sistema)
    show_generators(sistema)
    show_lines(sistema)
    sistema.resumo()  # ← insere aqui para checar tudo
