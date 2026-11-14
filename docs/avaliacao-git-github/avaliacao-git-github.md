# Avaliação prática — Git e GitHub

## 1. Objetivo e entrega

Avaliar o **processo de colaboração e integração com Git/GitHub**, não a sofisticação do código. Os estudantes podem usar agentes de código.

| Critério | Equipe de 3 | Equipe de 4 |
|---|---:|---:|
| Issues e PRs principais | 12 | 16 |
| Issues por estudante | 4 | 4 |
| Ciclos de integração | 4 | 4 |
| Aprovações por PR | 2 | 3 |
| Tags e releases mínimas | 12 de cada | 16 de cada |
| Vídeo máximo | 18 minutos | 24 minutos |

**Somente equipes de 3 e 4 pessoas serão permitidas**
**Prazo:** 9 dias corridos. **Entrega:** repositório principal público e vídeo da equipe. **Livro base:** *Learning Git*. CI/CD não é obrigatório.

## 2. Aplicação e arquivos

Criar um CRUD com **Web + CLI**, usando a mesma API REST e banco. A equipe escolhe a linguagem, o framework, o banco e o domínio.

| Arquivo de produção | Responsabilidade |
|---|---|
| `index.html` | Toda a Web, com HTML, CSS e JavaScript embutidos |
| `cli.py` (ou equivalente) | Toda a CLI |
| `api.py` (ou equivalente) | Endpoints e lógica da API |
| `db.py` (ou equivalente) | Acesso ao banco |
| `README.md` | Execução e documentação de cada issue |

**Arquivos por PR principal:**
- **Web:** `index.html`, API, banco e `README.md`.
- **CLI:** CLI, API, banco e `README.md`. Cada operação CLI tem endpoint próprio, diferente do endpoint Web. A CLI não acessa o banco diretamente.
- As funcionalidades Web devem ter suas próprias rotas e consultas SQL. Não reutilizar rotas ou consultas apenas para evitar alterar os arquivos exigidos.
- Toda PR principal inclui uma seção no README explicando a sua funcionalidade. A #1 explica como iniciar a Web; a #7, como usar a CLI.
- Não dividir código de produção em outros arquivos. Arquivos de testes, dependências, infraestrutura e configuração são permitidos sem limite, mas cada arquivo auxiliar criado ou alterado deve ser **listado e justificado na PR**.

## 3. Endpoints, autenticação e logs

### 3.1. Endpoints obrigatórios

| Operação | Web | CLI | Método |
|---|---|---|---|
| Healthcheck | `/api/web/health` | `/api/cli/health` | GET |
| Listar | `/api/web/records` | `/api/cli/records` | GET |
| Criar | `/api/web/records` | `/api/cli/records` | POST |
| Editar | `/api/web/records/{id}` | `/api/cli/records/{id}` | PUT |
| Excluir | `/api/web/records/{id}` | `/api/cli/records/{id}` | DELETE |
| Buscar | `/api/web/records/search` | `/api/cli/records/search` | GET |
| CSV | `/api/web/records/export` | `/api/cli/records/export` | GET |
| Indicadores | `/api/web/dashboard` | `/api/cli/dashboard` | GET |
| Alterar status (4 alunos) | `/api/web/records/{id}/status` | `/api/cli/records/{id}/status` | PATCH |
| Duplicar (4 alunos) | `/api/web/records/{id}/duplicate` | `/api/cli/records/{id}/duplicate` | POST |

`{id}` é o identificador do registro. Filtros, paginação e ordenação podem ser passados na query string. A implementação interna é livre.

### 3.2. Autenticação

- **Web (#1):** login por usuário e senha em `POST /api/web/login`.
- **CLI (#7):** obter token em `POST /api/cli/token` e enviar `Authorization: Bearer <token>` nos comandos protegidos. Permitir informar o token por variável de ambiente.
- Endpoints funcionais exigem autenticação. Sem credenciais ou com credenciais/token inválidos, responder **HTTP 401**. Os healthchecks podem ser públicos.
- Basta um usuário inicial configurável. Não exigir cadastro, recuperação de senha ou perfis.
- Não armazenar senha em texto puro nem registrar senhas, tokens ou segredos. A equipe define o mecanismo interno e documenta a configuração no README, sem publicar credenciais reais.

### 3.3. Logs

Cada operação Web ou CLI registra log **na API** e, se acessar o banco, também **no arquivo de acesso a dados** (inclusive leituras).

**Formato:** uma linha JSON por evento no stdout, visível com `docker compose logs`. Campos obrigatórios:

| Campo | Conteúdo |
|---|---|
| `timestamp` | Data/hora ISO 8601 UTC |
| `level` | `INFO`, `WARN` ou `ERROR` |
| `layer` | `api` ou `db` |
| `client` | `web` ou `cli` |
| `operation` | Nome da operação |
| `status` | `success` ou `error` |
| `request_id` | Mesmo valor para API e banco na mesma requisição |
| `message` | Descrição curta |

Exemplo — duas linhas da mesma operação:

`{"timestamp":"2026-11-06T22:30:00Z","level":"INFO","layer":"api","client":"cli","operation":"create","status":"success","request_id":"req-123","message":"Registro criado"}`
`{"timestamp":"2026-11-06T22:30:00Z","level":"INFO","layer":"db","client":"cli","operation":"insert","status":"success","request_id":"req-123","message":"Registro persistido"}`

Registrar sucessos e falhas de autenticação sem expor segredos. Não é necessário registrar SQL nem payload completo. Biblioteca livre. O README deve explicar como consultar logs. **Aceite:** logs correlacionados de uma operação Web e uma CLI que acessem o banco. Healthchecks não precisam acessar dados.

## 4. Docker Compose e testes

**Tudo roda exclusivamente pelo Docker Compose:** Web, API, banco, CLI, testes unitários e medição de cobertura.

- `docker compose up` inicia Web, API e banco.
- CLI e testes rodam em contêineres por `docker compose run` ou `docker compose exec`.
- O professor precisa apenas de **Docker e Docker Compose** no host, além de navegador e terminal. Não exigir Python, Node, Go, ferramentas de teste, banco ou bibliotecas instaladas fora dos contêineres.
- README com comandos completos para iniciar, autenticar, usar Web/CLI, preparar dados, consultar logs, executar testes e verificar cobertura.
- O professor clonará o `main` final e executará tudo localmente. O vídeo não substitui a execução.

**Testes unitários obrigatórios:**
- **Toda PR principal** entrega os testes unitários de suas alterações em CLI, API e banco, conforme aplicável.
- Exigir **100% de cobertura de linhas de todo o código desses arquivos já integrado**, inclusive código de PRs anteriores. Nas primeiras PRs, medir apenas arquivos existentes.
- O `index.html`, testes, infraestrutura e configuração **não entram** na cobertura obrigatória.
- Testes devem passar dentro dos contêineres. PRs corretivas que alterem arquivos cobertos também preservam testes e 100% de cobertura.
- Ferramentas/frameworks livres. Não exigir quantidade de testes, qualidade interna, cobertura de branches ou CI/CD.

## 5. Issues e critérios de aceite

Criar uma **spec** com as issues. Cada uma deve ter descrição, critérios de aceite, responsável, labels e milestone. **Cada integrante cria, assume e entrega 4 issues principais.**

**Equipe de 3:** issues #1–#12, distribuídas igualmente. **Equipe de 4:** issues #1–#16; o quarto integrante assume #13–#16, e os demais dividem #1–#12.

Cada issue principal exige **uma PR, aprovação dos colegas, testes, tag e release**. Respeitar também os arquivos, endpoints, login, logs e README das seções anteriores.

### Web — issues #1 a #6

| Issue | Entrega e aceite |
|---|---|
| **#1 — Estrutura Web** | Página inicial e login, API e banco, `GET /api/web/health` (HTTP 200), `POST /api/web/login` e usuário inicial. `docker compose up` funciona e README explica início/login |
| **#2 — Cadastro/edição** | Formulário com **4–6 campos**, pelo menos **4 obrigatórios**; validar campos e mostrar erros; criar/editar via API e banco; persistir dados |
| **#3 — Listagem/exclusão** | Tabela com **4 campos visíveis**, **5 itens por página**, ordenação, seleção e exclusão; dados carregados do banco ao abrir a página |
| **#4 — Busca avançada** | Pelo menos **3 filtros combináveis**, consulta assíncrona, atualização da tabela e limpeza dos filtros; filtros combinados retornam resultados corretos |
| **#5 — Exportação CSV** | Botão, endpoint e consulta; CSV inclui **todos os resultados filtrados**, não apenas a página atual; sem filtros, exporta todos |
| **#6 — Dashboard** | **3 gráficos** com dados reais do banco via API; atualizar valores ao recarregar; README explica os indicadores |

### CLI — issues #7 a #12

Cada PR CLI altera **CLI + API + banco + README**, com endpoints específicos e logs. A CLI não consulta o banco diretamente.

| Issue | Entrega e aceite |
|---|---|
| **#7 — Estrutura CLI** | Arquivo único, ajuda/subcomandos, `GET /api/cli/health`, `POST /api/cli/token` e Bearer token; funcionamento via Compose; acesso protegido sem token válido retorna **401** |
| **#8 — Cadastro/edição** | Comandos com os mesmos campos e validações da Web; registros persistidos e visíveis na Web |
| **#9 — Listagem/exclusão** | Paginação, ordenação e exclusão por identificador; alterações aparecem na Web |
| **#10 — Busca avançada** | Pelo menos **3 filtros combináveis**; mesmos parâmetros produzem resultados equivalentes aos da Web |
| **#11 — Exportação CSV** | Exportar resultados com filtros, não limitados à página atual; README informa como acessar o arquivo |
| **#12 — Indicadores** | Exibir em texto os mesmos **3 indicadores** e valores do dashboard Web |

### Exclusivas de equipes de 4 — issues #13 a #16

As quatro issues extras pertencem ao **quarto integrante**.

| Issue | Entrega e aceite |
|---|---|
| **#13 — Status Web** | Ativar/desativar registro via Web/API/banco; salvar o status |
| **#14 — Status CLI** | Ativar/desativar pelo endpoint CLI próprio; alteração aparece na Web |
| **#15 — Duplicação Web** | Criar cópia com ID próprio sem modificar o registro original |
| **#16 — Duplicação CLI** | Duplicar pelo endpoint CLI próprio; novo registro aparece na Web, original preservado |

A equipe escolhe **a ordem das issues**, respeitando dependências e os ciclos de integração.

## 6. Regras Git e GitHub

### 6.1. Forks, branches e PRs

- Cada estudante usa **fork próprio** e **git worktree** para suas quatro issues. Mostrar e explicar worktrees/branches no vídeo, sem precisar demonstrar comandos. Usar só branches, sem worktrees, reduz a nota; worktrees podem ser removidos após a apresentação.
- Cada PR deve apontar para o **`main` do repositório principal** (não apenas para o fork). PR principal é de autoria do responsável pela issue e usa **`Closes #N`** ou **`Fixes #N`**.
- **Todas as PRs**, inclusive corretivas, exigem aprovação registrada de **todos os colegas antes do merge**: 2 (equipe de 3) ou 3 (equipe de 4). Comentários e aprovação do autor não substituem essa regra.
- Usar o template obrigatório e justificar arquivos auxiliares na PR.

### 6.2. Quatro ciclos de integração

1. Existem **4 ciclos**. Cada integrante integra **1 PR principal por ciclo**.
2. **O ciclo seguinte só começa quando todos tiverem integrado uma PR principal no ciclo atual.**
3. A ordem dos **autores e issues é livre**, respeitando dependências e aprovações.
4. Conta a **autoria da PR integrada**, não quem fez o merge.
5. **PRs corretivas não contam nos ciclos** e podem ser integradas quando necessário, com aprovação dos demais. Não antecipam a PR principal seguinte.

| Equipe | Ciclo 1 | Ciclo 2 | Ciclo 3 | Ciclo 4 |
|---|---|---|---|---|
| 3 membros | A–C–B | B–A–C | C–B–A | A–B–C |
| 4 membros | A–C–D–B | D–A–B–C | B–D–C–A | C–B–A–D |

### 6.3. Merge e correções

- Após criar o repositório, **não fazer commits diretos no `main`**, inclusive para documentação/infraestrutura.
- Integrar **todas as PRs somente com Rebase and merge**. Proibidos merge commits, Squash and merge e force push no `main`. Histórico final **linear**.
- Rebase local e proteção do branch não são obrigatórios.
- Para corrigir algo após o merge, abrir **PR adicional** sem nova issue: usar **`Refs #N`**, explicar o motivo e obter aprovação de todos os outros. Não precisa alterar os quatro arquivos da PR principal. Não participa dos ciclos.

### 6.4. Tags e releases

- Após o merge de **cada PR principal**, criar **uma tag e uma release**.
- Tag aponta para o **commit do `main` resultante do merge**, não para o branch da feature.
- Tag segue **SemVer `vMAJOR.MINOR.PATCH`**, com versões únicas e crescentes na ordem dos merges; equipe decide os incrementos.
- A release identifica funcionalidade, issue e PR. A última corresponde ao `main` final funcionando.
- PRs corretivas não exigem tag/release. Tags/releases extras devem ser justificadas **no GitHub e no vídeo**.

## 7. PR, apresentação e avaliação

### 7.1. Conteúdo obrigatório da PR

Usar o template `docs/avaliacao-git-github/PULL_REQUEST_TEMPLATE.md` (manual ou copiado para `.github/PULL_REQUEST_TEMPLATE.md` da equipe). Informar:

- Descrição, issue (`Closes`/`Fixes` ou `Refs`), motivo de correções e arquivos alterados.
- Justificativa de infra/suporte, endpoints, logs e autenticação (quando aplicável).
- Comandos via Compose, testes executados, **100% de cobertura de linhas** e verificação funcional.

Descrição incompleta reduz a nota. Não é necessário anexar prints nem relatórios.

### 7.2. Vídeo

**Um vídeo** de até **18 min** (3 integrantes) ou **24 min** (4 integrantes). Cerca de **6 min por pessoa** é apenas sugestão. Exceder o limite reduz a **nota coletiva**.

Cada pessoa deve:
- Apresentar suas **4 issues/PRs**, correções, funcionalidades integradas e tags/releases.
- Explicar **uma PR revisada de cada colega**: o que verificou e por que aprovou.
- Mostrar e explicar **worktrees, branches e histórico de integração**, incluindo os ciclos.
- Relacionar as mudanças nos arquivos exigidos e na documentação.

Câmera **ligada durante a explicação**. Outra pessoa pode operar o computador. Não é necessário mostrar comandos Git. A apresentação é avaliada **individualmente**.

### 7.3. Avaliação

Serão considerados: issues e PRs, arquivos obrigatórios, aprovações, quatro ciclos, histórico linear, SemVer, funcionamento Web/CLI, autenticação/logs, testes com 100% de cobertura, execução integral via Compose e apresentação.

**Não geram pontos ou descontos:** quantidade de conflitos/commits, uso de agentes, sofisticação do código, qualidade/quantidade dos testes além dos requisitos objetivos, cobertura de branches e rebase local. É possível obter nota máxima sem conflitos.

## 8. Domínios sugeridos

Clientes, produtos, projetos, tarefas, eventos, startups, games ou modelos de LLM. O domínio deve comportar **4–6 campos**, **3 filtros** e dados para **3 gráficos**.

## 9. Dúvidas frequentes

- **Agentes de IA são permitidos?** Sim, sem desconto.
- **Há ordem obrigatória das issues?** Não; dependências e ciclos devem ser respeitados.
- **Posso dividir a implementação de uma issue em PRs de camadas?** Não.
- **Posso criar outros arquivos de produção?** Não; somente os quatro definidos. Testes/infra são permitidos com justificativa.
- **Como corrigir uma PR já integrada?** Nova PR com `Refs #N`, motivo, aprovação de todos e Rebase and merge; fora dos ciclos.
- **Preciso produzir conflitos ou demonstrar comandos Git?** Não. Mostre e explique worktrees e integração.
- **Posso criar versões extras?** Sim, justificadas no GitHub e no vídeo.
- **Como o professor verifica a aplicação?** Clona o `main` final e executa **tudo via Docker Compose**.
- **A apresentação de um integrante afeta a nota individual dos demais?** Não.
