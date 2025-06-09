# ⚡ power_opt – Otimização de Despacho de Geração Elétrica

Este projeto realiza a modelagem e simulação do despacho ótimo de geração elétrica em sistemas de potência, com suporte a múltiplas restrições operativas e funcionalidades configuráveis. A implementação é modular e construída com Pyomo, permitindo expansibilidade, análise de viabilidade (N-1) e comparação entre diferentes configurações operacionais.

## 📁 Estrutura do Projeto

```text
power_opt/
├── data/                  # Arquivos de entrada (JSON)
├── results/               # Resultados das simulações e gráficos
│   ├── csv/
│   └── figs/
├── power_opt/
│   ├── models/            # Classes base do sistema (barras, geradores, etc.)
│   ├── solver/            # Solver Pyomo e módulos auxiliares
│   │   ├── handler/       # Módulos de configuração, resultados e debug
│   │   ├── flags/         # Lógicas associadas às flags (rampa, perdas, etc.)
│   ├── utils/             # Utilitários diversos (leitura de dados, limpeza)
├── main.py                # Script principal de simulação
├── requirements.txt       # Dependências do projeto
├── pyproject.toml         # Configuração do Poetry
```

## 🚀 Funcionalidades Principais

- 📉 Despacho econômico e ambiental com ponderação entre custo e emissão.
- 🔁 Simulação de contingências N-1 (remoção de gerador ou linha).
- ♻️ Modelagem de perdas elétricas distribuídas nas barras.
- 🧮 Fluxo DC com rede de transporte e capacidade limitada por linha.
- 🔧 Restrições operativas como rampas de geração e limites técnicos.
- ❌ Modelagem explícita de déficit de carga.
- 📊 Geração automática de gráficos e relatórios.

## ⚙️ Instalação

### 1. Clone o repositório e entre no diretório

  ```bash
  git clone https://github.com/seu-usuario/power_opt.git
  cd power_opt
  ```

### 2. Crie o ambiente virtual com [Poetry](https://python-poetry.org/)

  ```bash
  poetry install
  ```

### 3. Ative o ambiente

  ```bash
  poetry shell
  ```

## 🧪 Como Executar

```bash
python main.py
```

Os arquivos de entrada são lidos de `data/`, e os resultados são salvos automaticamente em `results/csv/` e `results/figs/`.

## 🔍 Simulações N-1

O projeto executa automaticamente simulações de contingência para cada linha e gerador, removendo-os do sistema e avaliando:

- Viabilidade (sem déficit ou geração fictícia).
- Custo de operação (FOB).
- Impacto da contingência.

Gráficos são gerados em `results/figs/resultados_n_menos_1.png`.

## 📈 Gráficos Gerados

- FOB vs. δ com e sem perdas.
- Comparação de desempenho para cada configuração.
- Diagnóstico de viabilidade por cenário N-1.

## 📌 Requisitos

- Python ≥ 3.10
- Pyomo
- pandas, matplotlib, numpy
- Solver externo compatível (GLPK, HiGHS etc.)

## 📚 Créditos

Este projeto foi desenvolvido como parte dos estudos de otimização em sistemas elétricos, com foco em modularização, desempenho e clareza dos resultados.

## 👨‍💻 Autores

***Giovani Santiago Junqueira***
Mestrando em Engenharia de Sistemas Elétricos  

***Gabriel Halfeld Limp de Carvalho***
Mestrando em Engenharia de Sistemas Elétricos  

***Iuri Cristian Tanin Oliveira***
Mestrando em Engenharia de Sistemas Elétricos  
