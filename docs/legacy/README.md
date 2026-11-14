# videoDownloader
Eu estava querendo baixar uns videoclipes então tive a ideia de fazer isso.

Programa de terminal para baixar vídeos do YouTube em MP4 no Windows. Você cola um link, escolhe uma das resoluções disponíveis e recebe o arquivo na pasta **Downloads**. Para entender o funcionamento do código, leia o [guia passo a passo](GUIA_DO_CODIGO.md).

## Usar o executável

1. Abra `BaixarVideos.exe` com dois cliques.
2. Cole o link de um vídeo do YouTube e pressione Enter.
3. Escolha a resolução com as setas esquerda/direita (ou A/D) e confirme com Enter. Esc cancela a escolha daquele vídeo.
4. Aguarde a mensagem de conclusão. O MP4 será salvo na pasta Downloads configurada no Windows.
5. Cole outro link para continuar ou pressione Enter sem digitar nada para sair.

O computador precisa de acesso à internet. O executável já inclui Python, Node.js e FFmpeg; quem apenas vai usá-lo não precisa instalar essas ferramentas. Se não houver uma combinação MP4 com áudio para o vídeo, o programa mostrará um erro. Baixe apenas vídeos que você tem permissão para usar.

O arquivo gerado pelo projeto fica em `dist\BaixarVideos.exe`. A pasta `dist/` é ignorada pelo Git, então o executável precisa ser **gerado ou compartilhado separadamente**.

O banner aparece com uma breve animação e as escolhas são coloridas em terminais interativos. Para desativar as cores, defina a variável de ambiente `NO_COLOR`. Ao redirecionar a saída, o banner aparece imediatamente, sem códigos de cor.

### Opções pelo terminal

```powershell
.\dist\BaixarVideos.exe "https://youtu.be/ID_DO_VIDEO"
.\dist\BaixarVideos.exe "https://youtu.be/ID_DO_VIDEO" --saida "C:\Videos"
.\dist\BaixarVideos.exe "https://youtu.be/ID_DO_VIDEO" --verificar
```

`--saida` muda a pasta de destino. `--verificar` consulta os formatos sem baixar o vídeo; essa consulta não garante que a transferência posterior terá sucesso. Ao passar o link diretamente no terminal, o programa procura formatos até 1080p. No modo interativo, ele mostra as resoluções MP4 encontradas, inclusive acima de 1080p se estiverem disponíveis.

## Executar pelo código-fonte

No Windows, instale Python e uma [versão do Node.js com correções de segurança](https://nodejs.org/en/download). A compilação abaixo baixa o Node.js v24.22.1 LTS para `.tools/`, e `main.py` passa a usá-lo automaticamente. Na pasta do projeto, execute no PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py
```

Você também pode passar os mesmos argumentos do executável para `main.py`:

```powershell
.\.venv\Scripts\python.exe main.py "https://youtu.be/ID_DO_VIDEO" --saida "C:\Videos"
```

## Gerar o executável

Depois de criar `.venv` e instalar `requirements.txt` como mostrado acima, instale a ferramenta de compilação e execute o script:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-build.txt
.\build.ps1
```

O script baixa o Node.js v24.22.1 LTS do site oficial, verifica o SHA-256 publicado pela equipe do Node.js e inclui esse `node.exe` no aplicativo. Ele não altera o Node.js instalado no Windows. O resultado fica em `dist\BaixarVideos.exe`. As pastas `.tools/` e `build/` contêm arquivos intermediários e podem ser recriadas na próxima compilação.

## Arquivos do projeto e Git

| Caminho | Função | Git |
| --- | --- | --- |
| `main.py` | Código do aplicativo. | Versionado. |
| `requirements.txt` | Dependências para executar pelo Python. | Versionado. |
| `requirements-build.txt` | Dependência para gerar o `.exe`. | Versionado. |
| `build.ps1` | Comando de compilação recomendado. | Versionado. |
| `.venv/`, `.tools/`, `build/`, `dist/`, `test_download/` | Ambiente local, Node.js verificado, artefatos e vídeos de teste. | Ignorados pelo [`.gitignore`](.gitignore). |

Use `build.ps1` para gerar o executável em outro computador. A receita `.spec` é gerada em `build/` durante a compilação.
