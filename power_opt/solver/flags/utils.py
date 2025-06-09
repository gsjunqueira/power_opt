"""
Módulo `utils`

Contém utilitários comuns para os módulos de flags de modelagem condicional.

Este módulo visa padronizar e simplificar a verificação de ativação de funcionalidades
baseadas em configurações passadas no dicionário `system.config`.

Principal funcionalidade:
- Decorador `@flag_ativa(nome_flag)` que encapsula a verificação condicional
  diretamente na função `aplicar_*`, eliminando repetição de código.

Autor: Giovani Santiago Junqueira
"""

__author__ = "Giovani Santiago Junqueira"

def flag_ativa(nome_flag, system):
    """
    Decorador para ativar condicionalmente funções de modelagem com base em flags de configuração.

    Esse decorador verifica se a flag `nome_flag` está habilitada em `system.config`.
    Caso contrário, a função decorada não é executada.

    Args:
        nome_flag (str): Nome da flag booleana que controla a ativação da função.

    Returns:
        function: Função decorada com lógica condicional encapsulada.
    """
    return bool(system.config.get(nome_flag, False))

def safe_del(model, attr):
    """
    Remove com segurança um componente do modelo Pyomo, caso ele exista.

    Esta função é utilizada para evitar conflitos ao redefinir variáveis, parâmetros
    ou restrições em reconstruções iterativas do modelo. Se o atributo estiver presente
    no modelo, ele será removido explicitamente com `del_component()`.

    Args:
    -----
    model : ConcreteModel
        Instância do modelo Pyomo onde o componente pode existir.

    attr : str
        Nome do atributo a ser removido do modelo (ex: 'F', 'P', 'dual').
    """
    if hasattr(model, attr):
        model.del_component(getattr(model, attr))
