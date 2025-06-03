"""
Módulo `debug_handler`

Oferece ferramentas de depuração e análise interna dos resultados do modelo,
incluindo avaliação detalhada de perdas, geração, balanço de potência e função objetivo.

Autor: Giovani Santiago Junqueira
"""

__author__ = "Giovani Santiago Junqueira"

# pylint: disable=line-too-long, invalid-name
import csv
from pyomo.environ import value


def debug_perda_linha(debug_csv_path, modo_debug, linha_id, t, f, B, theta, G, perda, iteracao=None):
    """
    Exibe e (opcionalmente) salva os detalhes do cálculo de perda por linha.

    Args:
        debug_csv_path (str or None): Caminho do CSV de debug, se houver.
        modo_debug (bool): Ativa ou não a exibição no terminal.
        linha_id (str): ID da linha.
        t (int): Período de tempo.
        f (float): Fluxo da linha (pu).
        B (float): Susceptância da linha.
        theta (float): Diferença angular estimada.
        G (float): Condutância da linha.
        perda (float): Perda de potência (MW).
        iteracao (int, opcional): Número da iteração.
    """
    if not modo_debug:
        return

    msg = f"[DEBUG] Linha {linha_id} | t={t} | f={f:.6f} pu | B={B:.6f} | θ={theta:.6f} rad | G={G:.6f} → perda = {perda:.6f} MW"
    print(msg)

    if debug_csv_path:
        cabecalho = ["iteracao", "linha", "tempo", "f", "B", "theta", "G", "perda"] if iteracao is not None \
            else ["linha", "tempo", "f", "B", "theta", "G", "perda"]
        linha = [iteracao, linha_id, t, f, B, theta, G, perda] if iteracao is not None \
            else [linha_id, t, f, B, theta, G, perda]

        try:
            with open(debug_csv_path, "x", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(cabecalho)
                writer.writerow(linha)
        except FileExistsError:
            with open(debug_csv_path, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(linha)


def debug_geracao(model, system, modo_debug):
    """
    Exibe os valores de geração por gerador e tempo, se o modo debug estiver ativado.

    Args:
        model: Modelo Pyomo resolvido.
        system: Sistema com a base de potência.
        modo_debug (bool): Ativa ou não a exibição.
    """
    if not modo_debug:
        return
    print("\n[DEBUG] Geração por gerador:")
    for g in model.G:
        for t in list(model.T):
            p = value(model.P[g, t]) * system.base_power
            print(f"  {g} [t={t}] = {p:.4f} MW")


def debug_objetivo(model, modo_debug):
    """
    Exibe a decomposição da função objetivo, se o modo debug estiver ativado.

    Args:
        model: Modelo Pyomo resolvido.
        modo_debug (bool): Ativa ou não a exibição.
    """
    if not modo_debug:
        return

    custo_total = sum(value(model.P[g, t]) * model.custo[g] for g in model.G for t in model.T)
    emissao_total = sum(value(model.P[g, t]) * model.emissao[g] for g in model.G for t in list(model.T))
    fob = value(model.objetivo)
    print("\n[DEBUG] Decomposição da FOB:")
    print(f"  Custo total: {custo_total:.2f}")
    print(f"  Emissão total: {emissao_total:.2f}")
    print(f"  FOB total: {fob:.2f}")
    print(f"  Delta: {value(model.delta):.2f} | Peso emissão: {(1 - value(model.delta)):.2f} | Custo emissão: {value(model.custo_emissao):.2f}")


def debug_balanco_barras(model, system, considerar_fluxo, modo_debug):
    """
    Exibe o balanço de potência em cada barra e tempo, se o modo debug estiver ativado.

    Args:
        model: Modelo Pyomo resolvido.
        system: Objeto do sistema elétrico.
        considerar_fluxo (bool): Se o modelo inclui fluxo de potência.
        modo_debug (bool): Ativa ou não a exibição.
    """
    if not modo_debug:
        return
    print("\n[DEBUG] Balanço de potência por barra:")

    for b in model.B:
        for t in list(model.T):
            geradores_na_barra = [g.id for g in system.buses[b].generators]
            geracao = sum(value(model.P[g, t]) for g in geradores_na_barra)
            carga = value(model.demanda[b, t])
            entrada = sum(value(model.F[l, t]) for l in model.L if value(model.destination[l]) == b) if considerar_fluxo else 0.0
            saida = sum(value(model.F[l, t]) for l in model.L if value(model.origin[l]) == b) if considerar_fluxo else 0.0
            delta = geracao + entrada - saida - carga
            print(f"  Barra {b} [t={t}] → Geração = {geracao:.4f}, Carga = {carga:.4f}, Entrada = {entrada:.4f}, Saída = {saida:.4f}, Δ = {delta:+.6f}")

def extrair_debug(model, system, linha_id, t, f, B, theta, G, perda, considerar_fluxo, modo_debug=True) -> dict:
    """
    Retorna um dicionário com todos os dados de depuração do modelo.

    Args:
        model: Modelo Pyomo resolvido.
        system: Objeto com os dados do sistema elétrico.
        linha_id (str): Identificador da linha.
        t (int): Instante de tempo.
        f (float): Fluxo da linha (pu).
        B (float): Susceptância da linha.
        theta (float): Diferença angular (rad).
        G (float): Condutância da linha.
        perda (float): Perda de potência estimada (MW).
        considerar_fluxo (bool): Indica se o modelo considera fluxo de potência.
        modo_debug (bool): Se True, ativa exibição no terminal (opcional).

    Returns:
        dict: Dicionário com as informações de depuração:
              - objetivo
              - geracao
              - perda_linha
              - balanco_barras
    """
    return {
        "objetivo": debug_objetivo(model, modo_debug=modo_debug),
        "geracao": debug_geracao(model, system, modo_debug=modo_debug),
        "perda_linha": debug_perda_linha(
            debug_csv_path=None,
            modo_debug=modo_debug,
            linha_id=linha_id,
            t=t,
            f=f,
            B=B,
            theta=theta,
            G=G,
            perda=perda,
        ),
        "balanco_barras": debug_balanco_barras(
            model, system, considerar_fluxo=considerar_fluxo, modo_debug=modo_debug
        ),
    }
