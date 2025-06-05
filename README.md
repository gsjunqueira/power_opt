
# Power Optimization Models

Este repositório contém dois projetos distintos para otimização de despacho de geração elétrica:

---

## ⚙️ Projeto 1: Modelo Original (Arquivo Único)

Este projeto implementa um modelo de despacho de geração elétrica utilizando o Pyomo em um único arquivo principal (`modelo_pyomo.py`). Ele suporta diferentes configurações do sistema elétrico com base em *flags*, incluindo:

- Fluxo de potência linearizado (modelo DC)
- Perdas elétricas por linha
- Restrições de rampa para geradores térmicos
- Penalidades por emissão de CO₂
- Corte de carga modelado via geradores fictícios

### Execução
```bash
python main_1.py
```

---

## 🧩 Projeto 2: Modelo Refatorado (Modular)

Este projeto representa uma versão refatorada e modularizada do modelo anterior. O código foi reestruturado em múltiplos arquivos e pacotes para facilitar manutenção, testes e expansibilidade futura.

### Estrutura do Projeto
- `power_opt/models/`: definição de componentes do sistema (geradores, linhas, barras etc.) — **compartilhado**
- `power_opt/utils/`: utilitários auxiliares como carregamento e limpeza de dados — **compartilhado**
- `power_opt/solver/`:
  - `model_builder.py`: construção do modelo Pyomo
  - `pyomo_solver.py`: orquestrador principal
  - `handler/`: exportação de resultados, depuração e manipulação de configurações
  - `flags/`: lógica condicional para ativação de funcionalidades (fluxo, perdas, emissão, rampa, déficit)

### Execução
```bash
python main.py
```

---

## 📁 Dados e Resultados

- Dados de entrada: `data/`
- Resultados de simulações: `results/`, incluindo:
  - Tabelas CSV consolidadas por tipo de variável
  - Gráficos (geração, perdas, fluxos, déficit)
  - Arquivos de log e depuração detalhada por iteração

---

## 📌 Observações

- Ambos os projetos utilizam o solver **HiGHS** ou **GLPK** via Pyomo.
- Para reproduzir os experimentos com diferentes valores de `delta`, consulte os scripts `main_1.py` (original) e `main.py` (refatorado).
- O Projeto 2 substitui os geradores fictícios por variáveis explícitas de déficit e permite rastreamento modular de perdas, rampas e emissões.

---

## 👨‍💻 Autores

***Giovani Santiago Junqueira***
Mestrando em Engenharia de Sistemas Elétricos  

***Gabriel Halfeld Limp de Carvalho***
Mestrando em Engenharia de Sistemas Elétricos  

***Iuri Cristian Tanin Oliveira***
Mestrando em Engenharia de Sistemas Elétricos  
