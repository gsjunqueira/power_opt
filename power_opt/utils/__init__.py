"""
Pacote `utils`

Este pacote agrupa utilitários diversos utilizados no projeto `power_opt`.
Inclui funções de conversão de resultados, limpeza de diretórios e carregamento
de dados para o modelo de despacho ótimo de energia elétrica.

Módulos incluídos:
- `converter`: conversão de resultados para DataFrame estruturado
- `clean`: script principal para limpeza dos resultados
- `clean_handler`: funções auxiliares de limpeza
- `loader`: carregamento de dados do sistema

Autor: Giovani Santiago Junqueira
"""

__author__ = "Giovani Santiago Junqueira"

from .loader import DataLoader
from .clean import limpar_cache_py
from .clean_handler import limpar_diretorio
from .converter import preparar_dados_graficos, preparar_df, split_config, preparar_n_menos_1

__all__ = ["DataLoader", "limpar_cache_py", "limpar_diretorio",
           "preparar_dados_graficos", "preparar_df", "split_config",
           "preparar_n_menos_1"
           ]
