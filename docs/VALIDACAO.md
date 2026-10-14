# Validação técnica e critérios — CanaLoss

## Revisão de 13/10/2026 — resultado verificado

A auditoria partiu do commit `da42a3f5fcbc36a523afcd8cc2975bd835d6866e`. Foram lidos README, módulos Python, scripts SQL, testes, dados de exemplo, relatório, configuração local e workflow antes das alterações. O template foi comparado na versão `50e1e2720637b222357a7ebd1919c38a44af7cd2` de [agodoi/templateFiapVfinal](https://github.com/agodoi/templateFiapVfinal/tree/50e1e2720637b222357a7ebd1919c38a44af7cd2), incluindo README, documento acadêmico e orientações de pastas.

O código corrigido foi validado na [execução #3 do GitHub Actions](https://github.com/marcoshausen77/FIAP-FarmTech-CanaLoss/actions/runs/38449103702), commit **`1736551b213e41d94a38f5f1c02ca47dc72d86ec`**. Conclusão: **success**, em 13/10/2026 às 15h45 (America/Sao_Paulo), 18h45 UTC.

| Verificação | Resultado observado |
|---|---|
| Estado inicial, local | 85 aprovados e oito de integração não selecionados |
| Após as correções, local, Python 3.12.14 | **89 aprovados**, oito de integração não selecionados, em 0,16 s |
| Actions #3, job `unit`, Python 3.12.15 | **89 aprovados**, oito de integração não selecionados, em 0,65 s |
| Actions #3, criação do esquema | `Esquema Oracle disponível.` |
| Actions #3, job `oracle`, Python 3.12.15 | **97 aprovados, zero falhas e zero testes pulados**, em 0,98 s |
| Relatório de demonstração | Resultado gerado idêntico a `reports/exemplo.txt` |
| Compilação e dependências | `compileall` concluído; `pip check` sem incompatibilidades |

As durações correspondem às suítes, sem download ou inicialização do Oracle. As dependências verificadas foram `oracledb 3.4.2`, `python-dotenv 1.2.4` e `pytest 8.4.2`. Docker não está disponível no ambiente desta revisão local; a comprovação de conexão real, CRUD e integridade é a execução remota, não os testes locais.

Comando local utilizado:

```bash
python -m pytest -q -m 'not integration' --junitxml=test-results/final-unit.xml
```

Os logs dos jobs `unit` e `oracle` foram consultados após a conclusão. No Oracle, os oito casos de `tests/test_oracle.py` aparecem como PASSED. Os artefatos JUnit da execução estão publicados como `testes-unitarios` e `testes-oracle-real`. A execução #3 comprova o commit identificado; novos commits têm resultados próprios na [lista de execuções da branch main](https://github.com/marcoshausen77/FIAP-FarmTech-CanaLoss/actions/workflows/tests.yml?query=branch%3Amain).

## Classificação dos achados e tratamento

| Categoria solicitada | Achado confirmado | Tratamento |
|---|---|---|
| 1. Cumprimento do enunciado | O README não identificava explicitamente o Capítulo 6; os resultados precisavam distinguir demonstração fictícia e evidências atuais | Atividade explicitada; resultados conhecidos e rastreabilidade dos requisitos incluídos |
| 1. Cumprimento do enunciado | Validação JSON não cumpria integralmente a regra declarada contra notação exponencial | Correção pontual e três regressões, detalhadas abaixo |
| 2. Adequação ao template | Ausência de identidade visual, identificação acadêmica organizada e documento `document/ai_project_document_fiap.md` | Logotipo original e documento específico incluídos; cinco integrantes confirmados identificados |
| 2. Adequação ao template | `docs/VALIDACAO.md` dizia que o template não havia sido fornecido; faltava correspondência entre as estruturas | Referência atualizada e equivalências registradas no documento acadêmico |
| 3. Problema técnico real | `1e0`, `1e-4` e `1.00e1` em campos numéricos JSON eram normalizados antes da validação e aceitos | Verificação da grafia original pelo parser antes de construir `Decimal` |
| 3. Problema técnico real | Um conjunto válido de 10.000 talhões e 10.000 colheitas gerava JSON de 5.970.058 bytes, recusado pelo importador de 5 MiB | Tamanho UTF-8 validado antes da gravação; arquivo anterior preservado |
| 3. Inconsistência documental | README descrevia acesso privado e generalizava confirmações que não existem no cadastro de talhão | Visibilidade pública confirmada pela API; texto ajustado ao comportamento real |
| 3. Evidências desatualizadas | A aprovação histórica de 93 testes não comprovava o novo estado | Histórico preservado e nova execução identificada com commit e logs |
| 4. Melhorias opcionais | Autenticação, auditoria multiusuário, interface web, sensores, modelos de IA e filtros adicionais | Não implementadas; fora do escopo desta revisão |
| 4. Organização opcional | Mover configurações e SQL apenas para repetir nomes de pastas | Não realizado; os papéis de `config/` e `scripts/` foram mapeados sem quebrar os caminhos existentes |

Nenhuma fórmula, funcionalidade de menu, esquema Oracle ou workflow precisou ser reescrito. Os testes existentes foram mantidos. Não foi criado outro repositório nem alterada a visibilidade.

### Regressões acrescentadas

`tests/test_files_cli.py` ganhou três casos parametrizados para números exponenciais e um teste de limite de exportação. O último verifica bytes UTF-8 com acentos, rejeição acima do limite, preservação do conteúdo anterior e exportação/reimportação exatamente no limite. Assim, a suíte passou de 85 para 89 testes sem banco, mantendo os oito testes Oracle: total de 97.

### Cálculos e arquivos de exemplo

A revisão leu `examples/dados.json`, recalculou as duas colheitas e comparou o TXT gerado com o arquivo versionado. Foram confirmados 40 t de perda, 2.380 t de produção total estimada e R$ 6.000,00 de impacto. O percentual consolidado é `40 / 2380 × 100`, exibido como 1,68%; a recuperação hipotética de 15% é 6 t e R$ 900,00. As regras de denominador zero, precisão, limites, ranking e alertas são verificadas pela suíte de domínio.

### Links, imagem e credenciais

Os caminhos relativos e âncoras Markdown foram conferidos. As referências acadêmicas foram abertas nas fontes indicadas: texto de Rosa et al., registro da Embrapa e documentação do driver. Os links Oracle foram fixados na documentação 3.4.2, correspondente ao driver testado. O PNG foi validado e é idêntico, byte a byte, ao `assets/logo-fiap.png` do template; não depende de hospedagem externa para aparecer no README.

Foi feita inspeção dos arquivos versionados e busca por chaves privadas, formatos de tokens, arquivos `.env` e atribuições de senha no histórico alcançável. Não foram encontradas credenciais reais nesses arquivos. `.env.example` contém valores ilustrativos e o workflow contém somente credenciais `CI_Disposable` do Oracle temporário. A revisão não adicionou segredos. A verificação é limitada ao conteúdo deste repositório; não presume acesso a configurações privadas externas.

## Histórico anterior — preservado para rastreabilidade

### Execução local de 12/10/2026

Python 3.12.14; oracledb 3.4.2; python-dotenv 1.2.4; pytest 8.4.2.

Comando, executado na raiz do projeto:

```bash
python -m pytest -q -m 'not integration' --junitxml=test-results/local-unit.xml
```

Resultado: **84 passed, 6 deselected**. Os seis casos de integração exigem Oracle real. Docker e socket Docker não estavam disponíveis no ambiente local; essa execução não comprova conexão Oracle.

### Integração contínua inicial

Primeira execução: [Actions #1](https://github.com/marcoshausen77/FIAP-FarmTech-CanaLoss/actions/runs/38313712996), commit `e9c02f6`.

O Oracle 23.26.3.0.0 iniciou, o esquema foi criado e a suíte executou: **89 aprovados e 1 falha**. A falha ORA-01466 ocorreu na fotografia de exportação com transação READ ONLY imediatamente após DDL. A consulta foi substituída por um único SELECT com LEFT JOIN, preservando a consistência entre tabelas. Foram acrescentados casos para precisão decimal, talhão sem colheita e fluxo completo de consultas, Insights, TXT, JSON e importação repetida pelo terminal. 

### Execução histórica aprovada — Actions #2

[GitHub Actions #2 — resultado completo](https://github.com/marcoshausen77/FIAP-FarmTech-CanaLoss/actions/runs/38336245433)

Código testado: `398521b1fee841fe9d0f616e3639e92fe0ca1b3e`.
Conclusão dos testes: 12/10/2026 às 23h20 (America/Sao_Paulo), equivalente a 13/10/2026 às 02h20 UTC.

| Ambiente | Comando | Resultado |
|---|---|---|
| Local, Python 3.12 | `python -m pytest -q -m "not integration" --junitxml=test-results/local-unit.xml` | 85 aprovados, 8 de integração não selecionados |
| GitHub, job unit | `python -m pytest -m "not integration" -v --junitxml=test-results/unit.xml` | Aprovado |
| GitHub, job oracle | `python main.py --init-db` | Esquema criado no Oracle real |
| GitHub, job oracle | `python -m pytest -v --junitxml=test-results/oracle.xml` com `RUN_ORACLE_TESTS=1` | **93 aprovados, sem falhas e sem testes pulados, em 0,89 s** |

O tempo de 0,89 s corresponde à suíte, não ao download ou à inicialização do contêiner. Os relatórios JUnit estão nos artefatos `testes-unitarios` e `testes-oracle-real` da execução. O Oracle temporário do CI é encerrado após os testes; o ambiente reproduzível para uso local está no Docker Compose.

Os oito testes reais verificaram:

1. Conexão, inclusão, consulta por segunda conexão, edição, exclusão e fotografia consistente.
2. Duplicidade de IDs/operações, chaves estrangeiras e restrições numéricas.
3. Rollback de um lote que falha depois de inserções válidas.
4. Importação/exportação JSON e conflito de cadastro existente.
5. Registros inexistentes e tratamento parametrizado de texto com aparência de SQL.
6. Cadastro e consulta pelos menus, com encerramento normal.
7. Talhão sem colheita, valores decimais mínimos e exportação da fotografia.
8. Consulta, alertas, simulações, TXT, JSON e rejeição de importação repetida pelo terminal.

A correção da falha inicial foi verificada no mesmo teste que antes falhava. A aprovação refere-se ao escopo implementado, não a certificação agronômica ou garantia de nota.

## Matriz de critérios

| Critério | Evidência |
|---|---|
| Linha lógica e problema concreto | Contexto, objetivos, entrada → validação → Oracle → resultados no README e no documento acadêmico |
| Relevância | Histórico e tradução da perda física em valor financeiro |
| Inovação | Ranking e cenários em `domain.simulate`; alertas configuráveis |
| Validação | `domain`, `files`, restrições SQL e casos negativos, incluindo as regressões JSON |
| Usabilidade | Menus em português, nova tentativa, confirmação, cancelamento e saída |
| Funções/procedimentos | Regras, relatórios e CRUD com parâmetros |
| Listas, tuplas e dicionários | Coleções de registros, menus, agrupamentos e cenários |
| Tabelas em memória | Resultado de `consolidated` |
| TXT | `export_txt`, arquivo de exemplo e teste de leitura |
| JSON | Round-trip, validação e importação atômica |
| Oracle | Repositório exclusivo Oracle e testes de integração real |
| GitHub e template | README com identidade FIAP, `document/ai_project_document_fiap.md` preenchido e equivalências de organização documentadas |
| Entrega | README, código, dependências, SQL, Compose, exemplos, testes e referências verificáveis; sem vídeo no escopo informado |

## Comparação final com o template

O [documento acadêmico](../document/ai_project_document_fiap.md) contém introdução, visão geral, desenvolvimento, resultados, conclusões, referências e anexos. As seções genéricas de IA foram adaptadas com indicação explícita de que treinamento e acurácia não se aplicam. Não foram inventados feedback de usuários, dados de campo ou resultados de modelos.

O README incorpora logotipo, identificação, descrição, estrutura, execução, resultados, histórico e atribuição. `src/`, `.github/`, `database/`, `tests/`, `examples/` e `reports/` foram preservados. Configurações continuam na raiz e scripts Oracle em `database/`, com justificativa no [Anexo B](../document/ai_project_document_fiap.md#anexo-b--adequação-ao-template). As referências ao template indisponível e ao acesso privado foram corrigidas.

## Condições de entrega e pendências acadêmicas

O prazo de **14/10/2026** foi informado pelo aluno. A revisão ocorre em 13/10/2026. O [arquivo `src/readme.md` do template](https://github.com/agodoi/templateFiapVfinal/blob/50e1e2720637b222357a7ebd1919c38a44af7cd2/src/readme.md) orienta considerar o último commit dentro do prazo e atribuir alterações posteriores à próxima sprint. Não foi encontrado impedimento à revisão antes dessa data nas condições disponíveis.

A identificação dos cinco integrantes do Grupo 83 foi confirmada em 13/10/2026 e atualizada no [README](../README.md#integrantes-confirmados) e no [documento acadêmico](../document/ai_project_document_fiap.md). Kelly e Murilo foram registrados com os nomes fornecidos, sem acrescentar sobrenomes.

Permanecem somente as informações que exigem confirmação do aluno ou da equipe:

1. Confirmar professor, tutor ou coordenador se essa identificação for exigida pela turma. O proprietário do template não foi automaticamente declarado professor do grupo.
2. Conferir no portal o horário exato de encerramento, eventuais condições adicionais e o protocolo de envio. Esta revisão não acessou o portal acadêmico nem realizou a submissão.

O repositório está público, e não há pendência de alteração de visibilidade. O template está disponível e foi aplicado. O enunciado fornecido do Capítulo 6 não exige vídeo. A aprovação técnica não substitui a avaliação acadêmica nem comprova a entrega no portal.
