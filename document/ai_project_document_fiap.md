<p align="center">
  <a href="https://www.fiap.com.br/"><img src="../assets/logo-fiap.png" alt="FIAP — Faculdade de Informática e Administração Paulista" width="280"></a>
</p>

# Documento acadêmico — CanaLoss

**Sistema Inteligente de Monitoramento de Perdas Financeiras na Colheita de Cana-de-Açúcar**

FIAP · Tecnólogo em Inteligência Artificial · FarmTech Solutions · Grupo 83

**Atividade:** Capítulo 6 — Python e além. **Revisão:** 13/10/2026.

| Integrante confirmado | RM |
|---|---|
| Marcos Rodrigues Czerner Hausen | 576709 |

A relação completa dos integrantes e os nomes de professor, tutor ou coordenador dependem de confirmação da equipe. Não foram atribuídos nomes ou vínculos profissionais sem confirmação.

Este documento adapta o [modelo disponibilizado pelo professor](https://github.com/agodoi/templateFiapVfinal/blob/50e1e2720637b222357a7ebd1919c38a44af7cd2/document/ai_project_document_fiap.md) ao sistema efetivamente implementado. O CanaLoss usa regras determinísticas e cálculos; as seções de treinamento de modelos e avaliação preditiva não se aplicam.

## Sumário

1. [Introdução](#c1)
2. [Visão geral do projeto](#c2)
3. [Desenvolvimento](#c3)
4. [Resultados e avaliações](#c4)
5. [Conclusões e trabalhos futuros](#c5)
6. [Referências](#c6)
7. [Anexos](#c7)

<a id="c1"></a>
## 1. Introdução

### 1.1. Escopo e contexto

O agronegócio compreende produção, processamento, distribuição e comercialização. O CanaLoss delimita sua atuação à colheita de cana-de-açúcar e ao acompanhamento econômico de perdas estimadas. A literatura sobre agricultura digital contextualiza o uso de informação e computação nas cadeias produtivas (Massruhá et al., 2020).

Na colheita mecanizada, parte da matéria-prima pode permanecer no campo. Rosa et al. (2009) estudam perdas visíveis em uma situação experimental específica. O trabalho fundamenta o problema e o uso da produção acrescida da massa perdida como denominador do percentual. O programa não transforma os resultados desse estudo em uma taxa universal.

O problema é a dispersão de registros de área, produção, perda e preço, que dificulta identificar quais operações concentram maior impacto financeiro. O público precisa de uma visão histórica consistente e de resultados com unidades explícitas.

### 1.2. Relação com Inteligência Artificial

O projeto integra um curso de Inteligência Artificial, mas esta entrega trabalha fundamentos de Python e persistência de dados. Não há modelo estatístico treinado, classificação aprendida, API de IA, inferência preditiva ou ajuste automático de parâmetros. O termo “inteligente” no nome da solução identifica a organização dos dados para apoiar decisões. Os alertas decorrem de limites escolhidos pelo usuário.

### 1.3. Solução desenvolvida e justificativa

A aplicação Python de terminal cadastra talhões e operações de colheita, calcula perdas físicas e financeiras e armazena o histórico no Oracle. O módulo CanaLoss Insights apresenta ranking por impacto, alertas e cenários de recuperação. Importação/exportação JSON e relatório TXT permitem transportar registros e compartilhar resultados.

A solução é relevante por traduzir uma medição física em valor econômico e manter os dados de origem verificáveis. O resultado é uma estimativa de receita bruta associada à perda, não uma apuração contábil ou comprovação de economia.

<a id="c2"></a>
## 2. Visão geral do projeto

### 2.1. Objetivos

**Objetivo geral:** apoiar o monitoramento das perdas estimadas de colheita, com histórico íntegro e informações compreensíveis.

- Validar cadastros, números, unidades, datas e referências entre registros.
- Calcular perdas em toneladas, percentual e valor monetário.
- Consultar, corrigir e comparar operações, preservando a área histórica.
- Ordenar impactos financeiros e simular reduções relativas das perdas.
- Demonstrar funções, procedimentos, listas, tuplas, dicionários, tabelas em memória, TXT, JSON e conexão real com Oracle.

### 2.2. Público-alvo e abrangência

Produtores de cana e responsáveis por acompanhar a colheita são os usuários pretendidos. O protótipo é acadêmico, de operação local e individual. A comunicação usa português, datas DD/MM/AAAA e valores monetários em reais. Não houve implantação em uma propriedade ou pesquisa com usuários finais.

### 2.3. Metodologia e fluxo implementado

O desenvolvimento separa regras de negócio, persistência, arquivos e interface. O fluxo parte da digitação ou importação dos dados, passa pela validação, grava uma transação no Oracle e calcula resultados a partir do histórico consultado. Uma falha na importação desfaz o lote inteiro. Cálculos e apresentação permanecem separados para evitar arredondamento prematuro.

A avaliação combina revisão do código, dados fictícios com resultados conhecidos, testes negativos de entrada, testes da interface e integração com Oracle real no GitHub Actions. A comparação com o template usa a versão `50e1e2720637b222357a7ebd1919c38a44af7cd2`, consultada em 13/10/2026.

<a id="c3"></a>
## 3. Desenvolvimento

### 3.1. Tecnologias e componentes

| Componente | Implementação |
|---|---|
| Python 3.12 | Aplicação e testes |
| `decimal` e `dataclasses` | Precisão decimal e modelos validados `Talhao` e `Colheita` |
| `json`, `pathlib`, `tempfile` e `os` | Arquivos UTF-8 e substituição atômica |
| `python-oracledb` em modo Thin | Conexão e SQL parametrizado, sem Oracle Instant Client |
| `python-dotenv` | Leitura de configuração local não versionada |
| Oracle Database Free e Docker Compose | Banco relacional real com volume persistente |
| pytest e GitHub Actions | Testes unitários, de interface e de integração |

As dependências aceitas estão em [requirements.txt](../requirements.txt). A validação atual usou `oracledb 3.4.2`, `python-dotenv 1.2.4` e `pytest 8.4.2`. Os comandos completos para Windows e Linux/macOS estão em [instalação e execução](../README.md#instalação-e-execução).

| Camada | Responsabilidade |
|---|---|
| [main.py](../main.py) | Inicializar aplicação ou criar tabelas ausentes com `--init-db` |
| [src/cli.py](../src/cli.py) | Menus, confirmação, cancelamento e nova tentativa |
| [src/domain.py](../src/domain.py) | Validações, modelos, cálculos, ranking, cenários e alertas |
| [src/oracle.py](../src/oracle.py) | Conexão, CRUD, transações e fotografia consistente dos dados |
| [src/files.py](../src/files.py) | Contrato JSON e gravação atômica |
| [src/reports.py](../src/reports.py) | Relatório, agregação e apresentação de números |

### 3.2. Modelagem dos dados e algoritmos

#### 3.2.1. Dados de entrada

| Campo | Unidade ou formato | Regra principal |
|---|---|---|
| Identificadores | Até 30 caracteres | Letras maiúsculas, números, hífen e sublinhado; primeiro caractere alfanumérico |
| Nome do talhão | Texto de até 100 caracteres | Não vazio e sem caracteres de controle abaixo de U+0020 |
| Área | Hectares | Positiva; área integral da operação |
| Produção colhida | Toneladas | Não negativa |
| Perda estimada | kg/ha | Não negativa; informada a partir da medição externa |
| Preço de referência | R$/t | Positivo e informado por operação |
| Data | DD/MM/AAAA no terminal | Entre 01/01/1900 e a data atual |

O limite numérico é de 1.000.000.000, com até quatro casas decimais; trata-se de proteção técnica, não de parâmetro agronômico. O terminal usa vírgula decimal e admite pontos apenas para milhares agrupados. JSON usa ponto decimal, com exportação dos decimais como strings. Valores ausentes, booleanos, infinitos, NaN e notação exponencial não substituem números válidos.

#### 3.2.2. Fórmulas e tratamento dos casos extremos

Sejam `A` a área em ha, `L` a perda em kg/ha, `C` a produção colhida em t, `P` o preço em R$/t e `r` a redução relativa escolhida em %:

| Indicador | Fórmula |
|---|---|
| Perda física `Q` (t) | `A × L / 1.000` |
| Produção total estimada `T` (t) | `C + Q` |
| Percentual de perda | `100 × Q / T`, quando `T > 0` |
| Prejuízo estimado `V` (R$) | `Q × P` |
| Recuperação hipotética (t) | `Q × r / 100` |
| Recuperação hipotética (R$) | `V × r / 100` |

Quando `C = Q = 0`, o percentual é indefinido e exibido como N/D. Com produção zero e perda positiva, ele é 100%. O consolidado divide a soma das perdas pela soma das produções totais; não calcula média simples dos percentuais. Cada operação conserva seu próprio preço. Arredondamento `ROUND_HALF_UP` é aplicado somente à apresentação.

O ranking agrupa as operações por talhão e ordena o prejuízo de forma decrescente; empates são ordenados pelo identificador. O alerta seleciona operações cujo percentual seja maior ou igual ao limite escolhido. A simulação reduz uma fração da perda original, sem confundir redução relativa com pontos percentuais.

#### 3.2.3. Oracle e integridade

| Entidade | Atributos |
|---|---|
| `TALHOES` | `id` (PK), `nome`, `area_ha` |
| `COLHEITAS` | `id` (PK), `talhao_id` (FK), `data`, `area_ha`, `producao_t`, `perda_kg_ha`, `preco_t` |

Um talhão pode ter várias colheitas. A chave estrangeira impede registros órfãos e exclusão de talhões com histórico. A restrição UNIQUE de talhão/data impõe uma operação consolidada por dia. As restrições CHECK complementam as validações numéricas. A data máxima é verificada no Python porque depende do dia atual.

A área do talhão é copiada no registro da colheita e permanece imutável naquele histórico. Alterar o cadastro não recalcula o passado. Campos derivados, como prejuízo, não são duplicados em colunas. O esquema está em [database/schema.sql](../database/schema.sql), e as operações estão em [database/operacoes.sql](../database/operacoes.sql) e `src/oracle.py`.

As instruções usam bind variables. Cada operação de escrita confirma a transação somente ao concluir e executa rollback em caso de erro. A inicialização DDL é separada, pois o Oracle confirma DDL implicitamente. A exportação lê as duas tabelas em um único SELECT com LEFT JOIN, preservando consistência e incluindo talhões sem colheita.

#### 3.2.4. Estruturas em memória e arquivos

Listas guardam registros e cenários; tuplas representam opções de menu e o par de listas retornado por `snapshot`; dicionários guardam indicadores e agrupamentos. `consolidated` devolve uma tabela em memória como lista de dicionários. Funções e procedimentos recebem parâmetros, como `calculate(record)`, `simulate(records, percentages)`, `export_json(path, talhoes, colheitas)` e `export_txt(path, records)`.

O JSON versão 1 tem somente `versao`, `talhoes` e `colheitas`, até 10.000 itens por lista e até 5 MiB. A leitura verifica estrutura, duplicação de chaves e IDs, campos extras/ausentes, datas e referências internas. A importação é aditiva e transacional: conflitos com o Oracle cancelam todo o lote. A exportação valida o tamanho em bytes UTF-8 antes de substituir um arquivo existente. O TXT apresenta os dados de origem, totais e ranking. Ambos usam escrita em arquivo temporário seguida de substituição atômica.

### 3.3. Treinamento e testes

**Treinamento não se aplica.** Não existe conjunto de treino, validação de modelo ou métrica de acurácia. Os dados de [examples/dados.json](../examples/dados.json) são fictícios e destinam-se exclusivamente a demonstração e conferência de cálculos.

Os testes de software verificam resultados conhecidos, dados inválidos, precisão, casos de zero, arquivos corrompidos, preservação de arquivo em caso de falha, navegação e cancelamento. Os oito testes Oracle conectam a um banco real: verificam CRUD, persistência por segunda conexão, restrições, transações, importação, exportação e fluxo de terminal. São usados IDs exclusivos e limpeza dos registros de teste. Mocks de interação não substituem o banco nos testes de integração.

<a id="c4"></a>
## 4. Resultados e avaliações

### 4.1. Resultados funcionais reproduzíveis

| Indicador | C001 | C002 | Consolidado |
|---|---:|---:|---:|
| Área da operação (ha) | 10 | 20 | 30 |
| Produção colhida (t) | 780 | 1.560 | 2.340 |
| Perda estimada (t) | 20 | 20 | 40 |
| Produção total estimada (t) | 800 | 1.580 | 2.380 |
| Perda (%) | 2,50 | 1,27 | 1,68 |
| Prejuízo estimado (R$) | 3.000,00 | 3.000,00 | 6.000,00 |

Esses resultados foram recalculados a partir do JSON de exemplo e comparados integralmente com [reports/exemplo.txt](../reports/exemplo.txt), sem divergências. A área total de 30 ha corresponde apenas aos dois talhões distintos desse exemplo; somar áreas de operações históricas repetidas não representa área física única.

| Redução relativa hipotética | Recuperação consolidada (t) | Valor bruto potencial (R$) |
|---|---:|---:|
| 5% | 2 | 300,00 |
| 15% | 6 | 900,00 |
| 30% | 12 | 1.800,00 |

Os valores são cenários matemáticos. Custos de intervenção, transporte, processamento, qualidade e ATR não estão deduzidos. Não se demonstrou que essas reduções sejam atingíveis no campo.

### 4.2. Evidências técnicas

Em 13/10/2026, a [execução #3 do GitHub Actions](https://github.com/marcoshausen77/FIAP-FarmTech-CanaLoss/actions/runs/38449103702) validou o commit `1736551b213e41d94a38f5f1c02ca47dc72d86ec`:

| Ambiente | Resultado verificado |
|---|---|
| Local, Python 3.12.14 | 89 testes aprovados; oito de integração não selecionados |
| Actions, job `unit`, Python 3.12.15 | 89 aprovados; oito de integração não selecionados |
| Actions, job `oracle`, Python 3.12.15 | **97 aprovados, zero falhas e zero testes pulados**, incluindo oito integrações com Oracle real |

O job Oracle criou o esquema e executou a suíte em 0,98 s, sem incluir nesse tempo a inicialização do contêiner. O detalhamento, o histórico de erros corrigidos e a matriz de critérios constam de [docs/VALIDACAO.md](../docs/VALIDACAO.md). Novos commits disparam o mesmo workflow; o resultado mais recente pode ser conferido em [Actions](https://github.com/marcoshausen77/FIAP-FarmTech-CanaLoss/actions/workflows/tests.yml?query=branch%3Amain).

### 4.3. Avaliação de usabilidade e feedback

Os testes verificam menus em português, mensagens de erro recuperáveis, unidades explícitas, confirmação em operações sensíveis, cancelamento e encerramento normal. Essas evidências são testes funcionais de interface, não uma pesquisa de usabilidade com produtores. **Não há feedback documentado de usuários finais**, portanto não foram atribuídos relatos, satisfação ou benefícios observados em campo.

<a id="c5"></a>
## 5. Conclusões e trabalhos futuros

No escopo avaliado, o CanaLoss atende ao objetivo de registrar operações, preservar histórico no Oracle e calcular impactos e cenários de forma reproduzível. A divisão em camadas e os testes permitem relacionar os requisitos acadêmicos a comportamentos executáveis. As correções desta revisão eliminaram a aceitação indevida de alguns números exponenciais no JSON e a possibilidade de exportar um arquivo acima do limite de reimportação.

As limitações incluem dependência da qualidade da amostragem, operação local sem autenticação multiusuário ou auditoria de alterações, ausência de custos e ATR no cálculo e impossibilidade de registrar vários turnos do mesmo talhão/dia separadamente. O programa não identifica causas, não recomenda regulagem de máquinas e não garante redução de perdas.

Trabalhos futuros possíveis são validar o fluxo com usuários reais, definir backup e controle de acesso para uso operacional, investigar filtros temporais e incorporar custos mediante requisitos confirmados. Sensores, interface web e aprendizado de máquina seriam novos projetos de evolução, não funcionalidades desta entrega. A revisão não os implementou.

<a id="c6"></a>
## 6. Referências

- ROSA, Eduardo José da; JOSÉ, Jefferson Vieira; SALVESTRO, Alexandre de Castro; GAVA, Ricardo. **Perdas visíveis de cana-de-açúcar em colheita mecanizada**. Encontro Internacional de Produção Científica Cesumar, 2009. [Texto integral](https://www.unicesumar.edu.br/epcc-2009/wp-content/uploads/sites/77/2016/07/jefferson_vieira_jose3.pdf). Acesso em 13 out. 2026.
- MASSRUHÁ, S. M. F. S. et al. (ed.). **Agricultura digital: pesquisa, desenvolvimento e inovação nas cadeias produtivas**. Brasília, DF: Embrapa, 2020. 406 p. [Registro institucional](https://www.alice.cnptia.embrapa.br/handle/doc/1126213). Acesso em 13 out. 2026.
- ORACLE. **python-oracledb 3.4.2: Managing Transactions**. [Documentação](https://python-oracledb.readthedocs.io/en/v3.4.2/user_guide/txn_management.html). Acesso em 13 out. 2026.
- ORACLE. **python-oracledb 3.4.2: Using Bind Variables**. [Documentação](https://python-oracledb.readthedocs.io/en/v3.4.2/user_guide/bind.html). Acesso em 13 out. 2026.
- VENZL, Gerald. **Oracle Database Free container images**. [Documentação do mantenedor](https://github.com/gvenzl/oci-oracle-free). Acesso em 13 out. 2026. Imagem comunitária utilizada: `gvenzl/oracle-free:23-slim-faststart`.
- FIAP. **MODELO GIT FIAP — templateFiapVfinal**. [Versão consultada](https://github.com/agodoi/templateFiapVfinal/tree/50e1e2720637b222357a7ebd1919c38a44af7cd2). Acesso em 13 out. 2026. Estrutura e documento adaptados para o CanaLoss; atribuição do material de origem em [README](../README.md#atribuição-do-template).

<a id="c7"></a>
## 7. Anexos

### Anexo A — Material executável e evidências

- [Esquema Oracle](../database/schema.sql) e [operações SQL](../database/operacoes.sql).
- [Dados de demonstração](../examples/dados.json) e [relatório TXT correspondente](../reports/exemplo.txt).
- [Suíte de testes](../tests/) e [workflow de integração](../.github/workflows/tests.yml).
- [Matriz de critérios e histórico de validação](../docs/VALIDACAO.md).

### Anexo B — Adequação ao template

| Elemento do modelo | Aplicação no CanaLoss |
|---|---|
| Identidade FIAP e nome do projeto | Cabeçalho, logotipo e nome completo no README e neste documento |
| Grupo, integrantes e professores | Grupo 83 e integrante confirmado; informações não verificadas registradas como pendentes |
| Descrição e execução | Contexto, justificativa, objetivos, recursos, instalação e exemplo no README |
| `document/ai_project_document_fiap.md` | Documento preenchido, com as sete partes do modelo |
| `src/` | Código fonte existente preservado |
| `config/` | Papel atendido por `.env.example`, `docker-compose.yml` e `pytest.ini` na raiz, mantidos por compatibilidade |
| `scripts/` | Papel atendido por `database/*.sql` e `main.py --init-db`, sem duplicar scripts |
| `.github/` | Workflow de testes existente preservado |
| `assets/` | Logotipo original fornecido no template |
| `document/other/` | Evidências complementares permanecem em `docs/VALIDACAO.md`, vinculadas ao documento |
| Histórico e atribuição | Histórico real de commits e crédito ao template, sem versões fictícias |
| Modelagem, treinamento e acurácia de IA | Modelagem de dados e algoritmos determinísticos; treinamento e acurácia declarados não aplicáveis |
| Feedback dos usuários | Ausência explicitada, sem depoimentos inventados |

As equivalências de `config/`, `scripts/` e `document/other/` preservam a organização funcional e os caminhos existentes. Não foram copiadas instruções genéricas nem criados diretórios vazios.
