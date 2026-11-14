# Plano das 16 issues — equipe de 4

As issues #1–#16, as labels e os milestones `Ciclo 1` a `Ciclo 4` já foram criados no GitHub. `User 1`, `User 2`, `User 3` e `User 4` são nomes provisórios; substitua por contas GitHub reais e atribua cada issue quando conhecê-las. As 16 issues foram criadas pela conta Murilo751 a pedido do usuário; isso **não cumpre** o critério de que cada estudante crie suas próprias quatro issues. Cada pessoa ainda precisa assumir e entregar quatro issues. Cada issue principal precisa de uma PR própria, com `Closes #N`, aprovação dos outros três colegas, testes, cobertura de 100%, tag e release após o merge. Esta lista não substitui essas ações no GitHub.

## Ciclo 1

### #1 — Estrutura Web e login
**Responsável:** User 1. **Labels:** `web`, `api`, `banco`, `autenticacao`. **Milestone:** `Ciclo 1`.

**Descrição:** Criar a página inicial, API, banco, usuário inicial configurável e Compose. Alterar `index.html`, `api.py`, `db.py` e `README.md`.

**Aceite:** `docker compose up` inicia Web, API e banco; `GET /api/web/health` retorna 200; `POST /api/web/login` autentica sem guardar senha em texto puro; endpoint protegido retorna 401 sem sessão; README explica iniciar e entrar; logs e testes das camadas alteradas.

### #7 — Estrutura CLI e token
**Responsável:** User 3. **Labels:** `cli`, `api`, `banco`, `autenticacao`. **Milestone:** `Ciclo 1`. **Depende de:** #1.

**Descrição:** Criar CLI em arquivo único, ajuda, subcomandos, healthcheck e token Bearer. Alterar `cli.py`, `api.py`, `db.py` e `README.md`.

**Aceite:** CLI roda por Compose; `GET /api/cli/health` retorna 200; `POST /api/cli/token` emite token; comandos protegidos aceitam token por `VIDEO_TOKEN` e devolvem 401 sem token válido; README mostra autenticação e uso; logs e testes.

### #2 — Cadastro e edição Web
**Responsável:** User 2. **Labels:** `web`, `api`, `banco`, `crud`. **Milestone:** `Ciclo 1`. **Depende de:** #1.

**Descrição:** Formulário de vídeo com título, URL, categoria, criador, duração e status; criar e editar pela API Web. Alterar `index.html`, `api.py`, `db.py` e `README.md`.

**Aceite:** Quatro campos obrigatórios e erros visíveis; POST/PUT Web persistem no banco; validação também na API; logs correlacionados e testes.

### #13 — Status Web
**Responsável:** User 4. **Labels:** `web`, `api`, `banco`, `status`. **Milestone:** `Ciclo 1`. **Depende de:** #2.

**Descrição:** Ativar e desativar registro na Web via `PATCH /api/web/records/{id}/status`. Alterar `index.html`, `api.py`, `db.py` e `README.md`.

**Aceite:** Estado salvo e recuperado após recarregar; resposta 404 para ID inexistente, 401 sem sessão; logs e testes.

## Ciclo 2

### #3 — Listagem e exclusão Web
**Responsável:** User 1. **Labels:** `web`, `api`, `banco`, `crud`. **Milestone:** `Ciclo 2`. **Depende de:** #2.

**Descrição:** Tabela carregada ao abrir, paginação, ordenação, seleção e exclusão. Alterar `index.html`, `api.py`, `db.py` e `README.md`.

**Aceite:** Pelo menos quatro colunas visíveis; cinco itens por página; ordenação funciona; exclusão pelo ID persiste; logs e testes.

### #8 — Cadastro e edição CLI
**Responsável:** User 2. **Labels:** `cli`, `api`, `banco`, `crud`. **Milestone:** `Ciclo 2`. **Depende de:** #2, #7.

**Descrição:** Comandos para criar e editar com os mesmos campos e validações da Web. Alterar `cli.py`, `api.py`, `db.py` e `README.md`.

**Aceite:** POST/PUT CLI próprios, sem acesso direto da CLI ao banco; registro aparece na Web; 401 sem token; logs e testes.

### #4 — Busca avançada Web
**Responsável:** User 3. **Labels:** `web`, `api`, `banco`, `busca`. **Milestone:** `Ciclo 2`. **Depende de:** #3.

**Descrição:** Filtrar por título, categoria e criador, combinando parâmetros; atualizar tabela sem recarregar. Alterar `index.html`, `api.py`, `db.py` e `README.md`.

**Aceite:** `GET /api/web/records/search`; filtros combinados corretos; botão para limpar; consulta assíncrona; logs e testes.

### #14 — Status CLI
**Responsável:** User 4. **Labels:** `cli`, `api`, `banco`, `status`. **Milestone:** `Ciclo 2`. **Depende de:** #7, #13.

**Descrição:** Comandos ativar/desativar via `PATCH /api/cli/records/{id}/status`. Alterar `cli.py`, `api.py`, `db.py` e `README.md`.

**Aceite:** Estado aparece atualizado na Web; endpoint CLI próprio; 401 sem token; logs e testes.

## Ciclo 3

### #5 — Exportação CSV Web
**Responsável:** User 1. **Labels:** `web`, `api`, `banco`, `csv`. **Milestone:** `Ciclo 3`. **Depende de:** #4.

**Descrição:** Botão e `GET /api/web/records/export`. Alterar `index.html`, `api.py`, `db.py` e `README.md`.

**Aceite:** CSV contém todos os resultados filtrados, além da página atual; sem filtros inclui todos; logs e testes.

### #9 — Listagem e exclusão CLI
**Responsável:** User 2. **Labels:** `cli`, `api`, `banco`, `crud`. **Milestone:** `Ciclo 3`. **Depende de:** #3, #8.

**Descrição:** Listar com paginação/ordenação e excluir pelo ID usando rotas CLI. Alterar `cli.py`, `api.py`, `db.py` e `README.md`.

**Aceite:** Cinco itens por página; ordenação; exclusão refletida na Web; 401 sem token; logs e testes.

### #10 — Busca avançada CLI
**Responsável:** User 3. **Labels:** `cli`, `api`, `banco`, `busca`. **Milestone:** `Ciclo 3`. **Depende de:** #4, #7.

**Descrição:** Comando de busca com título, categoria e criador combináveis e endpoint CLI próprio. Alterar `cli.py`, `api.py`, `db.py` e `README.md`.

**Aceite:** Mesmos parâmetros dão resultados equivalentes à Web; 401 sem token; logs e testes.

### #15 — Duplicação Web
**Responsável:** User 4. **Labels:** `web`, `api`, `banco`, `duplicacao`. **Milestone:** `Ciclo 3`. **Depende de:** #3.

**Descrição:** Botão de duplicação e `POST /api/web/records/{id}/duplicate`. Alterar `index.html`, `api.py`, `db.py` e `README.md`.

**Aceite:** Cópia tem ID novo; original preservado; 404 para ID inexistente e 401 sem sessão; logs e testes.

## Ciclo 4

### #6 — Dashboard Web
**Responsável:** User 1. **Labels:** `web`, `api`, `banco`, `dashboard`. **Milestone:** `Ciclo 4`. **Depende de:** #3.

**Descrição:** Três gráficos de registros por categoria, status e criador, via `GET /api/web/dashboard`. Alterar `index.html`, `api.py`, `db.py` e `README.md`.

**Aceite:** Dados reais do banco; valores mudam após recarregar; README explica indicadores; logs e testes.

### #11 — Exportação CSV CLI
**Responsável:** User 2. **Labels:** `cli`, `api`, `banco`, `csv`. **Milestone:** `Ciclo 4`. **Depende de:** #5, #10.

**Descrição:** Comando de exportação com filtros via `GET /api/cli/records/export`. Alterar `cli.py`, `api.py`, `db.py` e `README.md`.

**Aceite:** Todos os resultados filtrados no arquivo montado no host, além da página atual; README indica caminho; logs e testes.

### #12 — Indicadores CLI
**Responsável:** User 3. **Labels:** `cli`, `api`, `banco`, `dashboard`. **Milestone:** `Ciclo 4`. **Depende de:** #6, #7.

**Descrição:** Comando de indicadores via `GET /api/cli/dashboard`. Alterar `cli.py`, `api.py`, `db.py` e `README.md`.

**Aceite:** Exibe em texto os mesmos três indicadores e valores da Web; 401 sem token; logs e testes.

### #16 — Duplicação CLI
**Responsável:** User 4. **Labels:** `cli`, `api`, `banco`, `duplicacao`. **Milestone:** `Ciclo 4`. **Depende de:** #7, #15.

**Descrição:** Comando de duplicação via `POST /api/cli/records/{id}/duplicate`. Alterar `cli.py`, `api.py`, `db.py` e `README.md`.

**Aceite:** Cópia aparece na Web com ID novo; original preservado; 404 para ID inexistente e 401 sem token; logs e testes.
