"""
Módulo `clean_handler`

Contém funções auxiliares para remoção de arquivos de saída antigos e limpeza do diretório
de resultados.
Útil para garantir que os resultados gerados sejam atualizados e não se misturem com
execuções anteriores.

Autor: Giovani Santiago Junqueira
"""

__author__ = "Giovani Santiago Junqueira"

import os
import glob

def limpar_diretorio(caminho: str, extensoes: list[str] = None, excluir: list[str] = None):
    """
    Remove arquivos do diretório especificado com base nas extensões fornecidas.

    Args:
        caminho (str): Caminho da pasta a ser limpa.
        extensoes (list[str], opcional): Lista de extensões para remover, ex: ['.csv', '.png']
                                          Se None, remove todos os arquivos.
        excluir (list[str], opcional): Lista de nomes de arquivos a manter mesmo que coincidam
        com a extensão.
    """
    if not os.path.exists(caminho):
        print(f"⚠️  Diretório '{caminho}' não encontrado.")
        return

    excluir = excluir or []
    extensoes = extensoes or ["*"]  # Apaga tudo se nenhuma extensão for especificada

    for ext in extensoes:
        padrao = os.path.join(caminho, f"*{ext}")
        for arquivo in glob.glob(padrao):
            if os.path.basename(arquivo) in excluir:
                continue
            try:
                os.remove(arquivo)
                print(f"🧹 Arquivo removido: {arquivo}")
            except OSError as e:
                print(f"❌ Erro ao remover {arquivo}: {e}")
