# FIAP — Faculdade de Informática e Administração Paulista

<p align="center">
  <a href="https://www.fiap.com.br/"><img src="assets/logo-fiap.png" alt="FIAP — Faculdade de Informática e Administração Paulista" width="280"></a>
</p>

# CanaLoss — FarmTech Solutions

**Sistema Inteligente de Monitoramento de Perdas Financeiras na Colheita de Cana-de-Açúcar**

## Grupo 83

| Identificação acadêmica | Informação |
|---|---|
| Instituição | FIAP |
| Curso | Tecnólogo em Inteligência Artificial |
| Atividade | Capítulo 6 — Python e além |
| Projeto | FarmTech Solutions |
| Solução | CanaLoss |

### Integrantes confirmados

| Nome completo | RM |
|---|---|
| Marcos Rodrigues Czerner Hausen | 576709 |

A identificação dos demais integrantes do Grupo 83 ainda precisa ser confirmada pela equipe. Esta tabela não representa a composição completa do grupo.

### Professores

Os nomes do professor, tutor e coordenador desta atividade não foram confirmados. Nenhum nome ou perfil profissional foi atribuído por suposição.

## Descrição

O CanaLoss é uma aplicação Python de terminal que transforma registros de colheita em estimativas de perdas físicas e financeiras. O módulo **CanaLoss Insights** organiza prioridades e compara cenários hipotéticos de redução de perdas. Trata-se de apoio à decisão baseado em dados e regras matemáticas, não de um modelo de inteligência artificial.

Documentação: [documento acadêmico no modelo FIAP](document/ai_project_document_fiap.md) · [validação, critérios e histórico dos testes](docs/VALIDACAO.md) · [template de referência](https://github.com/agodoi/templateFiapVfinal).

## Contexto e problema

Na colheita mecanizada de cana-de-açúcar, matéria-prima pode permanecer no campo após a passagem da colhedora. O estudo de Rosa et al. (2009) avalia perdas visíveis em condições específicas de operação e utiliza a massa perdida em relação à produção acrescida das perdas. Seus resultados não devem ser generalizados como uma taxa universal para qualquer fazenda.

A agricultura digital envolve o uso de informação e ferramentas computacionais nas cadeias produtivas, conforme a obra organizada por Massruhá et al. (2020). Neste projeto, esse contexto é aplicado a um problema delimitado: consolidar o que foi colhido, estimar o que permaneceu no campo e traduzir essa diferença em impacto financeiro.

O problema atendido é a dificuldade de comparar registros dispersos e decidir quais áreas merecem investigação primeiro. Uma perda em toneladas, isoladamente, não mostra seu valor econômico; o preço de referência e a área precisam acompanhar cada operação. Nenhuma estatística nacional ou preço de mercado é presumido pelo sistema.

## Justificativa e objetivos

A organização dos registros permite relacionar perdas físicas a valores financeiros, preservar a área e o preço de cada operação e comparar impactos sem depender de anotações isoladas. Essa rastreabilidade justifica a solução para produtores e responsáveis pelo acompanhamento da colheita.

**Objetivo geral:** apoiar o acompanhamento das perdas estimadas na colheita de cana-de-açúcar, com histórico íntegro e resultados compreensíveis.

Objetivos específicos:

- Cadastrar talhões e operações, validando unidades, datas e limites.
- Calcular perda física, percentual e prejuízo estimado.
- Consultar históricos, comparar operações e ordenar impactos financeiros.
- Simular reduções relativas das perdas para apoiar a priorização.
- Manter os registros no Oracle e permitir intercâmbio JSON e relatórios TXT.

## Inovação aplicada

O diferencial, no escopo acadêmico, está na integração entre histórico, ranking financeiro, alertas configuráveis e comparação de cenários em uma interface simples. A relevância econômica é tornar o impacto estimado visível; a aplicação não demonstra por si só que uma intervenção é viável ou lucrativa. Não se reivindica ineditismo de mercado nem aprendizado de máquina.

## Funcionalidades

| Menu | Operações |
|---|---|
| Talhões | Cadastrar, consultar, editar nome/área e excluir somente sem colheitas vinculadas |
| Colheitas | Registrar, consultar histórico, filtrar por talhão, comparar dois registros, corrigir e excluir |
| CanaLoss Insights | Ranking, limite de alerta informado pelo usuário e três cenários de redução |
| Arquivos | Importar JSON validado, exportar fotografia consistente e gerar TXT |

Edições, exclusões, gravação de colheitas, importações e substituição de arquivos existentes exigem confirmação. O cadastro de talhão é salvo após a validação dos campos. A importação é aditiva: talhões idênticos podem ser reutilizados; conflitos de cadastro, IDs de colheita repetidos ou operações duplicadas cancelam o lote inteiro. Não há sobrescrita silenciosa do histórico.

## Fórmulas e unidades

Sejam `A` a área em hectares, `L` a perda estimada em kg/ha, `C` a produção efetivamente colhida em toneladas e `P` o preço informado em R$/t:

```text
Perda (t)             = A × L ÷ 1.000
Produção estimada (t) = C + Perda (t)
Perda (%)            = Perda (t) ÷ Produção estimada (t) × 100
Prejuízo (R$)         = Perda (t) × P
Recuperação (t)       = Perda (t) × redução (%) ÷ 100
Recuperação (R$)      = Prejuízo (R$) × redução (%) ÷ 100
```

Se produção e perda forem zero, o percentual é **N/D**, pois o denominador é zero. Produção zero com perda positiva resulta em 100%. Campos ausentes não são convertidos para zero.

Exemplo **inteiramente fictício**: 10 ha, 780 t colhidas, 2.000 kg/ha perdidos e R$ 150/t resultam em 20 t perdidas, 800 t totais estimadas, perda de 2,50% e prejuízo estimado de R$ 3.000,00. Reduzir essa perda em 15% representa 3 t e R$ 450,00 potencialmente recuperáveis. São valores brutos hipotéticos, sem custos de intervenção, transporte, processamento ou ajustes por qualidade/ATR.

O consolidado calcula o percentual pela soma das perdas dividida pela soma das produções totais, e não pela média simples dos percentuais. O preço de cada registro é preservado.

## Regras de dados

- Terminal: vírgula decimal; `1.250,50` significa 1250 unidades e 50 centésimos; `1.000` significa mil. Ponto decimal não é aceito no terminal.
- JSON: ponto decimal sem separador de milhares; exportação usa strings decimais para preservar precisão.
- Área e preço devem ser positivos; produção e perda podem ser zero.
- Números até 1.000.000.000, com no máximo quatro casas decimais. Limite técnico, não limite agronômico.
- NaN, infinito, booleanos, notação exponencial e texto numérico inválido são rejeitados.
- IDs: até 30 caracteres, letras maiúsculas, números, hífen e sublinhado. Nome: até 100 caracteres.
- Datas: entre 01/01/1900 e a data atual. Terminal usa DD/MM/AAAA; JSON usa AAAA-MM-DD.
- Uma operação consolidada por talhão e dia; cada registro representa a **área integral** do talhão. Operações parciais ou turnos devem ser consolidados antes da entrada.
- A área do cadastro é copiada para a colheita no registro. Alterar a área atual não recalcula operações históricas. Na importação, a área histórica pode diferir da atual legitimamente.
- JSON exige versão 1, estrutura exata, referências internas e IDs únicos; tamanho máximo de 5 MiB e até 10.000 itens por lista. Chaves repetidas e arquivos corrompidos são rejeitados.
- A exportação também respeita os 5 MiB, medidos em bytes UTF-8, para gerar um arquivo que possa ser reimportado. Se o limite for excedido, o arquivo de destino permanece intacto. JSON é um intercâmbio limitado; não substitui o backup de um banco maior.
- Importações usam uma transação única. Qualquer falha desfaz todas as inserções do lote.
- Alertas usam `perda percentual >= limite escolhido`. O limite não é apresentado como recomendação técnica universal.

## Tecnologias

Python 3.12, `decimal`, `dataclasses`, `json`, `pathlib`, `python-oracledb` (modo Thin), `python-dotenv`, pytest, Docker Compose, Oracle Database Free e GitHub Actions. Não é necessário instalar Oracle Instant Client no modo Thin.

## Estrutura de arquivos

| Caminho | Responsabilidade |
|---|---|
| [main.py](main.py) | Inicialização e opção `--init-db` |
| [src/domain.py](src/domain.py) | Modelos, validações, cálculos e Insights |
| [src/oracle.py](src/oracle.py) | Conexão, transações e CRUD Oracle |
| [src/files.py](src/files.py) | Importação/exportação JSON e escrita atômica |
| [src/reports.py](src/reports.py) | Relatórios e formatação brasileira |
| [src/cli.py](src/cli.py) | Menus e recuperação de erros de entrada |
| [database/schema.sql](database/schema.sql) | Tabelas, chaves e restrições |
| [database/operacoes.sql](database/operacoes.sql) | Referência das operações SQL parametrizadas |
| [tests/](tests/) | Regras, arquivos, interface e integração com Oracle real |
| [examples/dados.json](examples/dados.json) | Dados fictícios para demonstração |
| [reports/exemplo.txt](reports/exemplo.txt) | Relatório produzido com os dados fictícios |
| [document/ai_project_document_fiap.md](document/ai_project_document_fiap.md) | Documento acadêmico preenchido conforme o template |
| [docs/VALIDACAO.md](docs/VALIDACAO.md) | Evidências, auditoria e matriz de requisitos |
| [assets/logo-fiap.png](assets/logo-fiap.png) | Logotipo fornecido no template FIAP |
| [.env.example](.env.example) | Modelo de configuração local, sem credenciais reais |
| [docker-compose.yml](docker-compose.yml) | Serviço Oracle local e volume persistente |
| [requirements.txt](requirements.txt) e [pytest.ini](pytest.ini) | Dependências e configuração dos testes |
| [.github/workflows/tests.yml](.github/workflows/tests.yml) | Testes automáticos com Oracle temporário |

O template orienta separar documentação, configuração, scripts e código. `document/` contém o documento acadêmico e `src/` mantém o código. Os papéis de `config/` e `scripts/` já são atendidos pelos arquivos de configuração da raiz, por `database/` e por `main.py --init-db`. Esses caminhos foram preservados para manter os comandos e o workflow; não foram criadas pastas vazias ou cópias genéricas. A correspondência completa está no [anexo de adequação](document/ai_project_document_fiap.md#anexo-b--adequação-ao-template).

## Conteúdos de Python implementados

| Conteúdo | Implementação verificável |
|---|---|
| Funções com parâmetros | `calculate`, `simulate`, `number`, `export_json`, métodos do repositório |
| Procedimentos | `export_txt`, `run`, rotinas de cadastro e inicialização |
| Listas | Histórico, cenários, talhões e registros validados |
| Tuplas | Opções dos menus, retorno de `snapshot`, pares de alertas |
| Dicionários | Indicadores, payload JSON e agrupamento de resultados |
| Tabelas em memória | Lista de dicionários de `consolidated`, usada no ranking |
| TXT | `export_txt` produz relatório real em UTF-8 |
| JSON | Leitura, validação, importação transacional e exportação |
| Oracle | `connect`, CRUD parametrizado, PK, FK, CHECK e UNIQUE |

## Modelo Oracle

`TALHOES(id PK, nome, area_ha)` mantém o cadastro atual. `COLHEITAS(id PK, talhao_id FK, data, area_ha, producao_t, perda_kg_ha, preco_t)` guarda os dados históricos. A relação é um talhão para várias colheitas. A restrição UNIQUE impede duas operações no mesmo talhão/data e a FK impede excluir um talhão com histórico.

Os valores calculados são derivados dos dados de origem; não há colunas redundantes de prejuízo que possam ficar desatualizadas. Campos numéricos usam Oracle NUMBER e Python Decimal. SQL recebe valores por bind variables. O usuário da aplicação é próprio, criado pelo contêiner via APP_USER, e não SYS/SYSTEM.

As restrições numéricas são aplicadas no Python e no banco. A rejeição de datas futuras é da aplicação, porque depende da data corrente. A inicialização executa DDL separadamente das transações de dados, pois Oracle confirma DDL implicitamente. Não existe fallback para SQLite, JSON ou memória.

## Instalação e execução

Pré-requisitos: Git, Python 3.12 e Docker com Docker Compose v2. No Windows, iniciar o Docker Desktop com contêineres Linux. A imagem Oracle é grande e pode demorar no primeiro download; reservar memória e disco disponíveis para o banco, além do sistema operacional.

```bash
git clone https://github.com/marcoshausen77/FIAP-FarmTech-CanaLoss.git
cd FIAP-FarmTech-CanaLoss
python -m venv .venv
```

Ativar no Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
Copy-Item .env.example .env
```

Ou no Linux/macOS:

```bash
source .venv/bin/activate
cp .env.example .env
```

Editar `.env` e substituir as duas senhas ilustrativas. Manter `APP_USER=canaloss` e `ORACLE_DSN=localhost:1521/FREEPDB1` para o ambiente padrão. As senhas do `.env` configuram a primeira inicialização do volume; alterá-las posteriormente no arquivo não altera as senhas de um banco já criado.

```bash
python -m pip install -r requirements.txt
docker compose up -d --wait --wait-timeout 900
python main.py --init-db
python main.py
```

`--init-db` cria tabelas ausentes sem apagar as existentes; não é um mecanismo de migração de versões. Conferir a saúde com `docker compose ps`; investigar inicialização com `docker compose logs oracle`. Para parar sem remover os dados: `docker compose down`. Não usar `down -v` em um banco com dados que devam ser preservados.

O serviço fica vinculado apenas a `127.0.0.1:1521`, com volume persistente. `.env` e arquivos temporários estão ignorados pelo Git. O repositório está **público**, conforme verificação de 13/10/2026; colegas e avaliadores podem consultar seu conteúdo pelo link. A revisão não alterou a visibilidade.

## Exemplo de utilização

1. Iniciar Oracle, criar o esquema e abrir `python main.py`.
2. Menu 4 → 1: importar `examples/dados.json`; digitar SIM. Fazer isso uma única vez em um banco limpo.
3. Menu 1 → 2: visualizar os talhões fictícios.
4. Menu 2 → 2: consultar histórico, totais e ranking; menu 2 → 4: comparar C001 e C002.
5. Menu 3: informar limite `2` e cenários `5`, `15` e `30`. Explicar que são hipóteses.
6. Menu 4: exportar JSON e TXT para caminhos escolhidos.
7. Demonstrar validação digitando letras num campo numérico e uma data impossível; o programa permite nova tentativa. Usar V para cancelar número ou 0 nos demais campos.
8. Sair com 0. Os registros permanecem no Oracle.

Para repetir a importação em um banco já populado, o conflito será reportado e nenhum dado será duplicado. Não apague um volume com dados reais para repetir a demonstração.

### Resultados reproduzíveis do exemplo

| Indicador | C001 / T001 | C002 / T002 | Consolidado |
|---|---:|---:|---:|
| Produção colhida (t) | 780,0000 | 1.560,0000 | 2.340,0000 |
| Perda estimada (t) | 20,0000 | 20,0000 | 40,0000 |
| Produção total estimada (t) | 800,0000 | 1.580,0000 | 2.380,0000 |
| Perda (%) | 2,50 | 1,27 | 1,68 |
| Prejuízo estimado (R$) | 3.000,00 | 3.000,00 | 6.000,00 |

São saídas calculadas a partir de [dados fictícios](examples/dados.json), reproduzidas em [reports/exemplo.txt](reports/exemplo.txt). Não representam medições de uma fazenda ou resultados de implantação. Para redução relativa de 15%, o potencial bruto consolidado é de 6 t e R$ 900,00.

## Testes e evidências

O histórico aprovado anterior é a [execução #2 do GitHub Actions](https://github.com/marcoshausen77/FIAP-FarmTech-CanaLoss/actions/runs/38336245433), com 93 testes, incluindo oito testes de integração com Oracle real, no commit `398521b1fee841fe9d0f616e3639e92fe0ca1b3e`.

Na revisão de 13/10/2026, os 85 testes locais existentes passaram antes das alterações. Após corrigir dois problemas reproduzidos no JSON e acrescentar quatro casos de regressão, a execução local teve **89 aprovados e oito testes Oracle não selecionados**. Os resultados da integração atual e os respectivos commits estão em [docs/VALIDACAO.md](docs/VALIDACAO.md). O estado das novas execuções é consultável em [Actions](https://github.com/marcoshausen77/FIAP-FarmTech-CanaLoss/actions/workflows/tests.yml?query=branch%3Amain).

A [execução #3](https://github.com/marcoshausen77/FIAP-FarmTech-CanaLoss/actions/runs/38449103702) confirmou **97 testes aprovados, sem falhas nem testes pulados**, incluindo os oito testes com Oracle real, no commit `1736551b213e41d94a38f5f1c02ca47dc72d86ec`.

Executar dentro da pasta do projeto:

```bash
python -m pytest -m "not integration" -v
```

Para integração **em banco de desenvolvimento/teste**, depois de iniciar o Oracle:

```bash
# Linux/macOS
RUN_ORACLE_TESTS=1 python -m pytest -v
```

```powershell
# Windows PowerShell
$env:RUN_ORACLE_TESTS = '1'
python -m pytest -v
```

Sem `RUN_ORACLE_TESTS=1`, os testes Oracle ficam explicitamente pulados. Eles não são substituídos por mocks. Os testes unitários de interface isolam apenas a interação; os testes de persistência conectam ao Oracle e verificam commits com uma segunda conexão, integridade e rollback. Registros de teste recebem IDs exclusivos e são removidos ao final.

O workflow cria Oracle temporário, aguarda o healthcheck, instala dependências, cria o esquema e executa todos os testes. Credenciais com prefixo `CI_Disposable` existem apenas no contêiner descartável. Os resultados JUnit são publicados como artefatos.

Ver [evidências e conferência dos critérios](docs/VALIDACAO.md) e a aba [Actions](https://github.com/marcoshausen77/FIAP-FarmTech-CanaLoss/actions). Não confundir teste configurado com teste aprovado: o estado de cada execução está registrado ali.

## Limitações e cuidados de interpretação

O sistema depende de medições fornecidas pelo usuário. Não coleta sensores, não determina causas de perdas nem prescreve ajuste de máquinas. Perda estimada em kg/ha deve vir de amostragem adequada. Alterações de preço, qualidade, ATR, custos e perdas invisíveis não são modeladas. O ranking soma períodos e áreas distintos: maior impacto total não implica menor eficiência por hectare.

A solução é acadêmica e voltada à operação local. Não inclui autenticação multiusuário, auditoria de alterações ou edição de áreas históricas. Em produção, esses controles e backup do Oracle seriam necessários. Os limites de entrada são técnicos e não garantem plausibilidade agronômica.

## Referências

- ROSA, Eduardo José da; JOSÉ, Jefferson Vieira; SALVESTRO, Alexandre de Castro; GAVA, Ricardo. **Perdas visíveis de cana-de-açúcar em colheita mecanizada**. Encontro Internacional de Produção Científica Cesumar, 2009. [Texto integral](https://www.unicesumar.edu.br/epcc-2009/wp-content/uploads/sites/77/2016/07/jefferson_vieira_jose3.pdf). Consultado em 12 out. 2026. Fundamenta o problema e a relação entre massa perdida e produção acrescida das perdas; não define parâmetros universais do software.
- MASSRUHÁ, S. M. F. S. et al. (ed.). **Agricultura digital: pesquisa, desenvolvimento e inovação nas cadeias produtivas**. Brasília, DF: Embrapa, 2020. 406 p. [Registro institucional e obra](https://www.alice.cnptia.embrapa.br/handle/doc/1126213). Consultado em 12 out. 2026. Referência de contextualização da agricultura digital, não de estatísticas específicas de perdas de cana.
- ORACLE. **python-oracledb 3.4.2: Managing Transactions**. [Documentação](https://python-oracledb.readthedocs.io/en/v3.4.2/user_guide/txn_management.html). Consultado em 13 out. 2026.
- ORACLE. **python-oracledb 3.4.2: Using Bind Variables**. [Documentação](https://python-oracledb.readthedocs.io/en/v3.4.2/user_guide/bind.html). Consultado em 13 out. 2026.
- VENZL, Gerald. **Oracle Database Free container images**. [Documentação e tags](https://github.com/gvenzl/oci-oracle-free). Consultado em 12 out. 2026. Imagem comunitária documentada, não apresentada como imagem oficial da Oracle. Tag utilizada: `23-slim-faststart`, disponível na família de tags documentada; a execução do CI verifica seu download e funcionamento.
- FIAP. **Modelo de repositório e documento acadêmico**, disponibilizado em `agodoi/templateFiapVfinal`. [Template consultado](https://github.com/agodoi/templateFiapVfinal/tree/50e1e2720637b222357a7ebd1919c38a44af7cd2). Acesso em 13 out. 2026. Referência para identidade, organização e documentação.

## Histórico de desenvolvimento

Datas em America/Sao_Paulo. O histórico completo permanece nos [commits do repositório](https://github.com/marcoshausen77/FIAP-FarmTech-CanaLoss/commits/main).

| Data | Alteração verificável |
|---|---|
| 12/10/2026 | Implementação de terminal, Oracle, Insights, arquivos e testes (`e9c02f6`) |
| 12/10/2026 | Correção de consistência da exportação Oracle após DDL e aprovação de 93 testes (`398521b`) |
| 13/10/2026 | Correção da validação exponencial e do limite de exportação JSON; quatro regressões (`1736551`) |
| 13/10/2026 | Adequação acadêmica ao template, identidade FIAP e atualização das evidências |

## Atribuição do template

A organização documental foi adaptada do **MODELO GIT FIAP**, atribuído à FIAP no [template do professor](https://github.com/agodoi/templateFiapVfinal). O README de origem declara licença [Creative Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/). O logotipo foi copiado sem alteração do arquivo disponibilizado nesse template. Essa atribuição se refere ao material de origem; não foi definida uma licença própria para o código CanaLoss.

## Condições de entrega

O prazo informado para esta atividade é **14/10/2026**. A orientação em [src/readme.md do template](https://github.com/agodoi/templateFiapVfinal/blob/50e1e2720637b222357a7ebd1919c38a44af7cd2/src/readme.md) é considerar o último commit dentro do prazo; alterações posteriores ficam para a próxima sprint. Esta revisão foi realizada em 13/10/2026. O horário exato de encerramento e eventuais condições adicionais devem ser conferidos no portal da turma, ao qual esta revisão não teve acesso. O escopo informado do Capítulo 6 não exige vídeo.
