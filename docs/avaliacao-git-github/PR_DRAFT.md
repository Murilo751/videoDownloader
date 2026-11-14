## Descrição
- Adaptação inicial do antigo baixador para um catálogo de vídeos CRUD com Web, CLI, API REST e PostgreSQL. **Rascunho técnico:** a avaliação pede uma PR principal por issue; esta mudança conjunta não satisfaz esse critério histórico.

## Issue relacionada
- Refs #1, #2, #3, #4, #5, #6, #7, #8, #9, #10, #11, #12, #13, #14, #15, #16. Esta PR de preparação não usa `Closes`, pois cada issue requer sua própria PR principal.

## Motivo da correção (PR adicional)
- Não se aplica.

## Alterações realizadas
- Web (`index.html`): formulário, tabela paginada, filtros, CSV, gráficos, status e duplicação.
- CLI (`cli.py`): subcomandos de autenticação e CRUD, busca, CSV, indicadores, status e duplicação.
- API (`api.py`): endpoints Web e CLI, autenticação, validação, logs e CSV.
- Banco (`db.py`): esquema, consultas PostgreSQL e logs de leitura/escrita.
- Documentação (`README.md`): execução integral via Compose e plano de colaboração.

## Infraestrutura e suporte
- `Dockerfile`: imagem da API, CLI e testes.
- `compose.yaml`: orquestra Web, API, banco, CLI e testes.
- `nginx.conf`: serve a página e encaminha `/api/`.
- `requirements.txt`: dependências do contêiner.
- `tests/`: testes unitários de API, banco e CLI.
- `.github/workflows/tests.yml`: execução de testes via Compose em PRs.
- `.github/PULL_REQUEST_TEMPLATE.md`: template obrigatório de PR.
- `docs/avaliacao-git-github/`: enunciado, template original, plano das issues e este rascunho.
- `docs/legacy/`: cópia das alterações locais do baixador anterior para consulta.
- `.gitignore`: ignora exportações e dados de cobertura.

## Endpoints e logs
- Endpoints Web e CLI: health, login/token, records, search, export, dashboard, status e duplicate, cada qual com o prefixo correspondente.
- Logs JSON no stdout da API e da camada de dados, ligados por `request_id`.
- Consulta: `docker compose logs -f api`.

## Autenticação (quando aplicável)
- Web: cookie de sessão após `/api/web/login`. CLI: Bearer token após `/api/cli/token`.
- Rotas funcionais retornam HTTP 401 sem credencial válida. Healthchecks são públicos.

## Testes unitários e cobertura
- `tests/test_api.py`, `tests/test_db.py`, `tests/test_cli.py`.
- Comando: `docker compose run --build --rm tests`.
- **Resultado pendente:** o daemon Docker não iniciou neste ambiente; não há medição de cobertura validada. A configuração exige 100% e deve ser corrigida caso a execução revele linhas descobertas.
- A aplicação anterior não tinha suíte de testes integrada.

## Execução integral via Docker Compose
- Início: `$env:APP_PASSWORD = Read-Host "Senha inicial"; docker compose up --build -d`.
- CLI: `docker compose run --rm -it cli token admin`, seguido dos subcomandos com `VIDEO_TOKEN`.
- Testes/cobertura: `docker compose run --build --rm tests`.
- O host precisa somente de Docker/Compose, navegador e terminal.

## Verificação realizada
- `python -m py_compile api.py db.py cli.py tests/*.py` passou.
- `docker compose config --quiet` passou com `APP_PASSWORD` de teste.
- `node --check` do JavaScript embutido passou.
- Smoke test Flask com banco simulado passou para health, login/401 e leitura autenticada Web/CLI.

## Summary
```text
index.html ─┐
            ├─> api.py ─> db.py ─> PostgreSQL
cli.py ─────┘
```

## Evidence
- **Before:** aplicativo Windows de download, sem Web, API, banco, CLI REST ou Compose.
- **After:** rotas e clientes implementados; checagens de sintaxe/estrutura e smoke test locais passaram. Testes completos em Docker pendentes.

## Merge Danger
**Door:** two-way

**Blast Radius:** projeto inteiro

Substitui o fluxo anterior de download. A cópia está em `docs/legacy/`. Não integrar sem testes de Compose e sem separar as entregas por issue se o objetivo for cumprir integralmente o processo da avaliação.
