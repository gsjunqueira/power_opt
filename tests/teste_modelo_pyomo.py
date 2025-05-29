from power_opt.solver import PyomoSolver
from power_opt.utils import DataLoader

def main():
    # Carrega dados do sistema a partir do JSON
    sistema = DataLoader("data/dados_base.json").load_system()
    # sistema.resumo()  # ← insere aqui para checar tudo


    # Instancia e constrói o modelo
    solver = PyomoSolver(sistema,
                        considerar_fluxo=True,
                        considerar_perdas=True,
                        considerar_rampa=True,
                        considerar_emissao=True,
                        )
    solver.construir()
    # solver.model.pprint()

    # Resolve o modelo com o solver HiGHS
    solver.solve(solver_name="highs", tee=False)

#     # Exibe os resultados de geração e balanço
    solver.mostrar_resultados()
    solver.mostrar_balanco()

if __name__ == "__main__":
    main()
