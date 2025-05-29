# Otimizador de Despacho com e sem Perdas em Sistemas de Potência

Este projeto realiza a otimização do despacho de carga de um sistema elétrico, considerando ou não as perdas de transmissão, penalização por emissão de carbono e restrições operativas como limites de geração, rampa e capacidade de linhas. O modelo é implementado em Python com o uso do Pyomo (para formulação do modelo) e do solver HiGHS.

## Objetivos

- Resolver o problema de despacho de carga com ou sem consideração de perdas
- Avaliar a influência de um fator de penalidade `delta` associado à emissão de CO₂
- Simular condições de contingência (análise N-1)
- Gerar gráficos comparativos de desempenho (FOB vs Delta, FOB por cenário)

## Estrutura do Projeto

```text
projeto/
├── main.py                      # Script principal de execução
├── data/                   # Pasta com o arquivo de entrada de dados
│   ├── dados_base.json            # Dados do sistema (barras, geradores, linhas, cargas)
├── utils/                   # Pasta com o leitor dos dados de entrada
│   ├── loader.py                   # Leitura e estruturação dos dados
├── solver/                   # Pasta com o modelo de otimização
│   ├── modelo_pyomo.py            # Implementação do modelo de otimização (Pyomo)
├── models/                   # Pasta com os modelos de elementos do sistema
│   ├── base_generator.py
│   ├── bus.py
│   ├── fictitious_generator.py
│   ├── hydro_generator.py
│   ├── line.py
│   ├── load.py
│   └── __init__.py
├── results/
│   ├── resultados_otimizacao.csv  # Resultados gerais com perdas
│   ├── resultados_otimizacao_sem_perdas.csv # Resultados gerais sem perdas
│   ├── resultados_n_menos_1.csv   # Resultados dos cenários N-1
│   ├── comparacao_delta_vs_fob.png        # Gráfico: FOB com vs sem perdas
│   ├── resultados_delta_vs_fob.png        # Gráfico: FOB com perdas
│   ├── resultados_n_menos_1.png           # Gráfico: FOB por cenário N-1
```

## Requisitos

- Python 3.12+
- [Pyomo](http://www.pyomo.org/)
- [HiGHS solver](https://www.highs.dev/)
- pandas, matplotlib, numpy

Instalação recomendada com `poetry`:

```bash
poetry install
```

## Como Executar

1. Certifique-se de que o ambiente está ativado:

   ```bash
   poetry shell
   ```

2. Execute o script principal:

   ```bash
   python main.py
   ```

## Exemplos de Saída

### Gráfico FOB vs Delta com e sem Perda

![FOB comparado](comparacao_delta_vs_fob.png)

### Gráfico FOB vs Delta (Com Perda)

![FOB com perda](resultados_delta_vs_fob.png)

### FOB por Cenário de Contingência (Análise N-1)

![FOB N-1](resultados_n_menos_1.png)

## Contribuições

Este projeto faz parte de um estudo acadêmico e pode ser expandido para incluir:

- Modelagem hidroelétrica
- Otimização multiobjetivo
- Modelos estocásticos ou cenarizados

## Licença

Este projeto é de uso acadêmico e pode ser adaptado sob permissão expressa do autor.

---

> Desenvolvido por Giovani Santiago Junqueira, Gabriel Halfeld Limp de Carvalho e Iuri Cristian Tanin Oliveira | 2025
