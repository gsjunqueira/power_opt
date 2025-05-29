"""
Script clean.py

Remove todos os arquivos .pyc, .pyo e pastas __pycache__ do projeto.
Útil para evitar erros de importação causados por módulos antigos em cache.

Execução segura: pode rodar com o botão ▶️ no VS Code.
"""

import os
import shutil

def limpar_cache_py(diretorio_raiz="."):
    """
    Limpa arquivos .pyc, .pyo e pastas __pycache__ do diretório especificado.

    Parâmetros:
        diretorio_raiz (str): Caminho onde a limpeza deve começar (padrão: raiz do projeto).
    """
    for root, dirs, files in os.walk(diretorio_raiz):
        for nome in files:
            if nome.endswith((".pyc", ".pyo")):
                caminho_arquivo = os.path.join(root, nome)
                os.remove(caminho_arquivo)
                print(f"🧹 Removido arquivo: {caminho_arquivo}")
        for nome in dirs:
            if nome == "__pycache__":
                caminho_dir = os.path.join(root, nome)
                shutil.rmtree(caminho_dir)
                print(f"🧹 Removido diretório: {caminho_dir}")

    print("\n✅ Limpeza concluída.")
    limpar_terminal()

def limpar_terminal():
    """limpa o terminal após limpar o cache.py"""
    os.system('cls' if os.name == 'nt' else 'clear')

if __name__ == "__main__":
    limpar_cache_py()
