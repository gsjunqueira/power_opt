"""
Módulo `output_handler`

Responsável pela organização e formatação final dos dados gerados após a
otimização, preparando-os para exportação e análises posteriores.

Autor: Giovani Santiago Junqueira
"""

__author__ = "Giovani Santiago Junqueira"

import csv
from typing import Optional


def exportar_saida(
    resultados: Optional[dict] = None,
    duais: Optional[dict] = None,
    debug: Optional[dict] = None,
    caminho_base: Optional[str] = None
) -> None:
    """
    Exporta os resultados, variáveis duais ou informações de debug, 
    imprimindo em tela ou salvando em arquivos CSV conforme especificado.

    Args:
        resultados (dict, optional): Resultados principais da otimização.
        duais (dict, optional): Variáveis duais extraídas do modelo.
        debug (dict, optional): Informações de depuração interna.
        caminho_base (str or None): Caminho base para salvar arquivos. Se None, imprime em tela.
    """

    def salvar_em_csv(dados: dict, caminho_arquivo: str) -> None:
        """
        Salva os dados em um arquivo CSV com duas colunas: chave e valor.

        Args:
            dados (dict): Dicionário com os dados a serem salvos.
            caminho_arquivo (str): Caminho completo do arquivo de saída.
        """
        if not dados:
            return
        with open(caminho_arquivo, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["chave", "valor"])
            for k, v in dados.items():
                writer.writerow([k, v])

    def imprimir_em_tela(titulo: str, dados: dict) -> None:
        """
        Imprime os dados no terminal com título destacado.

        Args:
            titulo (str): Título da seção de dados.
            dados (dict): Dicionário a ser exibido.
        """
        print(f"\n--- {titulo} ---")
        for k, v in dados.items():
            print(f"{k}: {v}")

    if resultados is not None:
        if caminho_base:
            salvar_em_csv(resultados, f"{caminho_base}_resultados.csv")
        else:
            imprimir_em_tela("RESULTADOS", resultados)

    if duais is not None:
        if caminho_base:
            salvar_em_csv(duais, f"{caminho_base}_duais.csv")
        else:
            imprimir_em_tela("DUAIS", duais)

    if debug is not None:
        if caminho_base:
            salvar_em_csv(debug, f"{caminho_base}_debug.csv")
        else:
            imprimir_em_tela("DEBUG", debug)
