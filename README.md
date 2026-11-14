# Catálogo de vídeos

CRUD de links de vídeos com página Web, CLI, API REST e PostgreSQL. Este repositório foi adaptado dos requisitos em [`docs/avaliacao-git-github/avaliacao-git-github.md`](docs/avaliacao-git-github/avaliacao-git-github.md). O antigo baixador foi preservado em [`docs/legacy/`](docs/legacy/) para consulta, mas não integra a aplicação atual.

## Iniciar (somente Docker e Docker Compose)

No PowerShell, escolha uma senha local para o usuário inicial e inicie os três serviços:

```powershell
$env:APP_USERNAME = "admin"
$env:APP_PASSWORD = Read-Host "Senha inicial"
docker compose up --build -d
```

Abra `http://localhost:8080`, entre com o usuário e a senha escolhidos. A senha inicial é transformada em PBKDF2-SHA256 antes de entrar no banco; não é registrada em logs. Se o volume do banco já contiver esse usuário, mudar `APP_PASSWORD` não troca a senha persistida. Para uma instalação nova, use um volume novo. Não publique sua senha ou token no repositório.

## Usar a Web

A página carrega registros do banco após autenticar. O formulário cria e edita vídeos com título, URL, categoria, criador, duração em minutos e status. Os quatro primeiros campos são obrigatórios. A tabela mostra cinco registros por página, com ordenação, busca combinada por título/categoria/criador, exclusão, alteração de status e duplicação. O CSV exporta todos os registros que correspondem aos filtros, além da página atual. Os três gráficos contam registros por categoria, status e criador; os valores vêm do banco ao recarregar.

## Usar a CLI

Todos os comandos rodam em contêineres. Primeiro obtenha um token (a senha é solicitada sem aparecer no terminal):

```powershell
docker compose run --rm -it cli token admin
```

Copie o valor de `token` da resposta para uma variável de ambiente local:

```powershell
$env:VIDEO_TOKEN = "TOKEN_RECEBIDO"
docker compose run --rm cli health
docker compose run --rm cli list
docker compose run --rm cli create --title "Exemplo" --url "https://example.com/video" --category "Música" --creator "Canal" --duration-minutes 4
docker compose run --rm cli update 1 --title "Novo título" --url "https://example.com/video" --category "Música" --creator "Canal" --duration-minutes 5
docker compose run --rm cli search --title "Novo" --category "Música" --creator "Canal"
docker compose run --rm cli list --page 1 --sort title --direction desc
docker compose run --rm cli deactivate 1
docker compose run --rm cli activate 1
docker compose run --rm cli duplicate 1
docker compose run --rm cli dashboard
docker compose run --rm cli export --category "Música"
docker compose run --rm cli delete 1
```

O arquivo exportado fica em `exports/videos.csv` no host. `VIDEO_TOKEN` é entregue ao serviço `cli` via Compose; mantenha essa variável fora do repositório. Os comandos protegidos devolvem HTTP 401 sem token válido. O token vale 24 horas e é invalidado quando a API reinicia.

## Rotas

As rotas Web usam o prefixo `/api/web`; as rotas CLI usam `/api/cli`. Em cada prefixo há `GET /health`, `GET/POST /records`, `PUT/DELETE /records/{id}`, `GET /records/search`, `GET /records/export`, `GET /dashboard`, `PATCH /records/{id}/status` e `POST /records/{id}/duplicate`. A Web autentica em `POST /api/web/login` com cookie de sessão; a CLI em `POST /api/cli/token` com Bearer token. Healthchecks são públicos; as rotas funcionais exigem autenticação.

## Logs e testes

```powershell
docker compose logs -f api
docker compose run --rm tests
```

Cada linha de log da API ou do banco é JSON, com `timestamp`, `level`, `layer`, `client`, `operation`, `status`, `request_id` e `message`. Procure o mesmo `request_id` para correlacionar uma operação da API com seu acesso ao banco. O serviço de testes executa pytest e mede a cobertura de linhas de `cli.py`, `api.py` e `db.py`, exigindo 100%. `index.html`, testes e infraestrutura ficam fora dessa medição.

## Plano de colaboração

As [16 issues criadas](docs/avaliacao-git-github/ISSUES.md) têm descrição, aceite, responsáveis provisórios, labels, milestones e dependências. User 1, User 2, User 3 e User 4 são nomes provisórios; quando houver contas GitHub reais, atribua as issues. Elas foram criadas pela conta Murilo751 a pedido do usuário, o que não cumpre o critério de autoria individual. Há quatro ciclos, com uma PR principal por pessoa em cada ciclo; o ciclo seguinte começa após todos integrarem o atual. Cada estudante usa uma worktree por issue e abre PR para o `main` principal com `Closes #N`. Os outros três aprovam antes do merge. Use `Rebase and merge`; após cada PR principal, crie tag SemVer crescente no commit final de `main` e uma release que identifique issue, PR e funcionalidade. Correções posteriores usam PR adicional com `Refs #N` e aprovação dos três colegas. Nenhum desses eventos de colaboração é produzido automaticamente pelo código.

O template está em [`.github/PULL_REQUEST_TEMPLATE.md`](.github/PULL_REQUEST_TEMPLATE.md), com uma cópia em `docs/avaliacao-git-github/`. Arquivos auxiliares desta adaptação: `Dockerfile` (imagem da API, CLI e testes), `compose.yaml` (orquestração), `nginx.conf` (Web e proxy), `requirements.txt` (dependências), `tests/` (testes), `.github/` (template), `docs/avaliacao-git-github/` (enunciado, template e issues), `docs/legacy/` (cópia do aplicativo antigo). Liste e justifique esses arquivos na PR que os introduzir.
