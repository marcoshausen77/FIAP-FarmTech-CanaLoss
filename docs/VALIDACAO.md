# Validação técnica e critérios — CanaLoss

## Execução local de 12/10/2026

Python 3.12.14; oracledb 3.4.2; python-dotenv 1.2.4; pytest 8.4.2.

Comando, executado na raiz do projeto:

```bash
python -m pytest -q -m 'not integration' --junitxml=test-results/local-unit.xml
```

Resultado: **84 passed, 6 deselected**. Os seis casos de integração exigem Oracle real. Docker e socket Docker não estavam disponíveis no ambiente local; essa execução não comprova conexão Oracle.

## Integração contínua

Primeira execução: [Actions #1](https://github.com/marcoshausen77/FIAP-FarmTech-CanaLoss/actions/runs/38313712996), commit `e9c02f6`.

O Oracle 23.26.3.0.0 iniciou, o esquema foi criado e a suíte executou: **89 aprovados e 1 falha**. A falha ORA-01466 ocorreu na fotografia de exportação com transação READ ONLY imediatamente após DDL. A consulta foi substituída por um único SELECT com LEFT JOIN, preservando a consistência entre tabelas. Foram acrescentados casos para precisão decimal, talhão sem colheita e fluxo completo de consultas, Insights, TXT, JSON e importação repetida pelo terminal. Nova execução em conferência.

## Matriz de critérios

| Critério | Evidência |
|---|---|
| Linha lógica e dor específica | Contexto, objetivos e fórmulas no README |
| Relevância | Histórico e tradução da perda física em valor financeiro |
| Inovação | Ranking e cenários em `domain.simulate`; alertas configuráveis |
| Validação | `domain`, `files`, constraints SQL e casos negativos automatizados |
| Usabilidade | Menus em português, nova tentativa, confirmação, cancelamento e saída |
| Funções/procedimentos | Regras, relatórios e CRUD com parâmetros |
| Listas, tuplas e dicionários | Coleções de registros, menus, agrupamentos e cenários |
| Tabelas em memória | Resultado de `consolidated` |
| TXT | `export_txt`, arquivo de exemplo e teste de leitura |
| JSON | Round-trip, validação e importação atômica |
| Oracle | Repositório exclusivo Oracle e testes de integração real |
| GitHub | Código, documentação e workflow no repositório exclusivo |
| Entrega | README, código, dependências, SQL, Compose, exemplos e testes |

## Revisão da equipe

Confirmar a adequação ao template oficial da FIAP: ele não foi fornecido. A estrutura adotada é convencional, sem alegação de ser um template institucional. Confirmar também que os avaliadores e colegas têm acesso ao repositório privado. O escopo fornecido não exige vídeo.
