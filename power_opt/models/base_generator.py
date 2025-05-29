"""
base_generator.py

Define a classe abstrata BaseGenerator, que serve como interface comum para
diferentes tipos de geradores em um sistema elétrico de potência. Essa classe
pode ser estendida para modelar geradores térmicos, hidráulicos, eólicos,
fictícios ou outros.

Autor: Giovani Santiago Junqueira
"""

from abc import ABC, abstractmethod
from typing import Optional

class BaseGenerator(ABC):
    """
    Classe base abstrata para representar um gerador em um sistema elétrico.

    Esta classe define os atributos comuns a todos os tipos de geradores,
    incluindo limites de potência ativa e reativa, barra associada, tipo e
    status de operação.

    Subclasses devem implementar o método `get_power_output()` para fornecer
    a lógica específica da potência gerada em um determinado período.

    Args:
        id (str): Identificador único do gerador.
        bus: Objeto ou identificador da barra elétrica associada.
        gmin (float): Potência ativa mínima (MW).
        gmax (float): Potência ativa máxima (MW).
        qmin (Optional[float]): Potência reativa mínima (MVAr).
        qmax (Optional[float]): Potência reativa máxima (MVAr).
        type_ (str): Tipo do gerador (e.g., 'thermal', 'hydro', 'wind').
        fictitious (bool): Indica se o gerador é fictício (usado para balanceamento).
        status (bool): Indica se o gerador está em operação.

    Atributos:
        pg (float): Potência ativa atual (MW).
        qg (float): Potência reativa atual (MVAr).
    """

    def __init__(self, generator_id: str, bus, gmin: float = 0.0, gmax: float = 0.0,
                 qmin: Optional[float] = None, qmax: Optional[float] = None,
                 type_: str = "generic", fictitious: bool = False, status: bool = True):
        self.id = generator_id
        self.bus = bus
        self.gmin = gmin
        self.gmax = gmax
        self.qmin = qmin
        self.qmax = qmax
        self.pg = 0.0
        self.qg = 0.0
        self.type = type_
        self.fictitious = fictitious
        self.status = status

    @abstractmethod
    def get_power_output(self, period: int) -> float:
        """
        Método abstrato para retornar a potência ativa gerada no período especificado.

        Este método deve ser implementado pelas subclasses para calcular ou
        retornar a geração ativa correspondente a um período do horizonte de
        otimização ou simulação.

        Args:
            period (int): Índice do período a ser considerado.

        Returns:
            float: Potência ativa gerada (MW) no período especificado.
        """
