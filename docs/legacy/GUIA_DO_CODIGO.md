# Entendendo o videoDownloader, passo a passo

Este guia acompanha o código de [`main.py`](main.py). A ideia é que você consiga abrir os dois arquivos lado a lado e entender **o que acontece**, **qual função faz cada parte** e **por que as ferramentas externas são usadas**. Não é necessário conhecer todo o Python antes de começar.

## 1. O que o programa faz

O usuário fornece o link de um vídeo do YouTube. O programa consulta os formatos disponíveis, mostra as resoluções MP4, recebe uma escolha, baixa o vídeo e o áudio e salva o resultado na pasta Downloads do Windows.

```text
Abrir programa
    ↓
Informar link
    ↓
Consultar formatos com yt-dlp
    ↓
Escolher resolução
    ↓
Baixar vídeo e áudio
    ↓
Usar FFmpeg quando necessário
    ↓
Salvar arquivo MP4 em Downloads
```

O arquivo [`main.py`](main.py) implementa esse fluxo. [`requirements.txt`](requirements.txt) lista as bibliotecas necessárias para executá-lo pelo Python. [`build.ps1`](build.ps1) usa o PyInstaller para gerar o executável do Windows.

## 2. Comece pelo fim do arquivo: onde a execução inicia

No final de `main.py` está:

```python
if __name__ == "__main__":
    raise SystemExit(main())
```

Quando você executa `main.py` diretamente, o Python chama `main()`. Essa função devolve um número: `0` significa que terminou normalmente; `1` indica falha. `SystemExit` entrega esse número ao sistema operacional.

No `.exe`, o PyInstaller inicia esse mesmo código. Portanto, `main()` é o ponto de partida nos dois casos.

> **Como estudar:** encontre `main()` perto do fim de [`main.py`](main.py) e acompanhe as funções que ela chama. Você não precisa ler o arquivo apenas de cima para baixo.

## 3. `main()`: argumentos e modo de uso

`main()` usa `argparse` para aceitar estes argumentos:

| Argumento | O que faz |
| --- | --- |
| `url` | Link opcional. Se estiver ausente, o programa pede links no terminal. |
| `--saida PASTA` | Troca a pasta de destino. O padrão é Downloads. |
| `--verificar` | Consulta os formatos sem transferir o vídeo. |

Exemplos no terminal:

```powershell
.\dist\BaixarVideos.exe
.\dist\BaixarVideos.exe "https://youtu.be/ID_DO_VIDEO"
.\dist\BaixarVideos.exe "https://youtu.be/ID_DO_VIDEO" --saida "C:\Videos"
.\dist\BaixarVideos.exe "https://youtu.be/ID_DO_VIDEO" --verificar
```

Sem um link na linha de comando, `main()` mostra o logo e entra em um `while True`: pede um link, processa o vídeo e volta a pedir outro. Pressionar Enter com o campo vazio encerra o programa. Com um link passado como argumento, ele processa uma vez e termina.

### Como o programa encontra Downloads

`downloads_folder()` lê no registro do Windows o local configurado para Downloads. Isso também atende quem moveu a pasta para outro disco. Se a leitura falhar, usa `Path.home() / "Downloads"`.

`Path`, importado de `pathlib`, representa caminhos de arquivos. O método `destination.mkdir(parents=True, exist_ok=True)` cria a pasta de saída caso ela ainda não exista, quando um download vai começar.

## 4. Consulta das resoluções: `available_resolutions()`

No modo interativo, depois que você cola o link, `main()` chama `available_resolutions(url)`.

O trecho central é:

```python
with yt_dlp.YoutubeDL(
    {"js_runtimes": node_runtime(), "noplaylist": True, "quiet": True}
) as downloader:
    info = downloader.extract_info(url, download=False)
```

Aqui, `yt_dlp.YoutubeDL` cria o objeto que consulta o YouTube. `extract_info(..., download=False)` pede **informações sobre o vídeo**, mas ainda não baixa o arquivo. `noplaylist` evita processar uma playlist inteira. `quiet` reduz as mensagens dessa consulta.

O resultado `info` contém uma lista de formatos. A função procura formatos com imagem em MP4 e uma opção de áudio compatível, coleta as alturas (`height`) e devolve uma lista ordenada, como `[360, 720, 1080]`. Cada número representa a altura em pixels: `720` aparece para o usuário como `720p`.

Essa é uma **lista de possibilidades**, não uma garantia de que a transferência dará certo. Uma conexão interrompida ou um formato recusado pelo YouTube ainda pode causar erro na etapa do download. Se a lista ficar vazia, o programa informa que não encontrou resoluções MP4 com áudio.

### Por que aparece `node_runtime()`?

O `yt-dlp` pode precisar executar JavaScript para acessar formatos do YouTube. `node_runtime()` informa onde está o Node.js:

- Executando pelo Python, usa primeiro o Node.js verificado em `.tools/`, quando disponível; caso contrário, permite usar um runtime instalado no computador.
- Executando pelo `.exe`, aponta para o `node.exe` incluído dentro do pacote.

O teste `getattr(sys, "frozen", False)` distingue o programa empacotado pelo PyInstaller do script executado normalmente. `sys._MEIPASS` é a pasta temporária onde o PyInstaller disponibiliza os arquivos incluídos no `.exe` durante a execução.

## 5. Escolha da qualidade: `choose_resolution()`

`main()` passa a lista de alturas para `choose_resolution(heights)`.

Se houver uma única resolução, ela é selecionada automaticamente. Se houver várias, o programa começa na **maior**. No terminal interativo do Windows, as setas esquerda e direita mudam a escolha; Enter confirma e Esc cancela aquele vídeo. As teclas `a` e `d` também mudam a seleção. Fora desse tipo de terminal, ele mostra opções numeradas.

A função devolve um número, por exemplo `720`, ou `None` quando a escolha é cancelada. `main()` só inicia `download_video()` se recebeu uma altura.

## 6. Download: `download_video()`

Essa função reúne as configurações passadas ao `yt-dlp`. As mais importantes são:

```python
options = {
    "format": format_for_height(height) if height else FORMAT,
    "external_downloader": {"m3u8": "ffmpeg"},
    "ffmpeg_location": ffmpeg,
    "js_runtimes": node_runtime(),
    "merge_output_format": "mp4",
    "noplaylist": True,
    "outtmpl": str(destination / "%(title)s [%(id)s].%(ext)s"),
}
```

| Opção | Significado |
| --- | --- |
| `format` | Regra para escolher os fluxos de vídeo e áudio. |
| `external_downloader` | Usa FFmpeg para transferir fluxos do tipo `m3u8`. |
| `ffmpeg_location` | Caminho do FFmpeg fornecido por `imageio_ffmpeg`. |
| `js_runtimes` | Configuração do Node.js feita por `node_runtime()`. |
| `merge_output_format` | Pede MP4 como formato do arquivo resultante. |
| `outtmpl` | Nome do arquivo: `Título [ID].extensão`. |

O YouTube frequentemente oferece imagem e som em fluxos separados. Na expressão de formato, `bv` significa *best video* e `ba` significa *best audio*. O sinal `+` pede os dois fluxos; o FFmpeg pode uni-los no arquivo final. As barras `/` separam alternativas: se a primeira combinação não estiver disponível, o `yt-dlp` tenta a seguinte.

`format_for_height(height)` procura a altura exata escolhida na interface. Ele dá preferência a certas combinações de MP4 e áudio M4A. Se você passou um link diretamente na linha de comando, não houve escolha interativa; nesse caso é usado `FORMAT`, que procura formatos até 1080p.

Depois de configurar tudo, esta linha inicia a transferência:

```python
result = downloader.download([url])
```

O arquivo é salvo na pasta de destino com um nome semelhante a `Meu vídeo [abc123].mp4`. Se `--verificar` estiver ativo, a função consulta os formatos pedidos e termina **sem chamar** `download()`.

### Uma diferença importante entre os dois modos

No modo interativo, `available_resolutions()` não filtra alturas acima de 1080p. Se o YouTube oferecer uma resolução maior em MP4, ela pode aparecer no seletor. O limite de 1080p descrito em `FORMAT` vale para o modo em que o link é passado diretamente como argumento. Essa diferença está no código atual.

## 7. Como os erros são tratados

`download_video()` captura erros de download, de arquivo e de execução e mostra uma mensagem em vez de encerrar com uma exceção técnica. Para um erro HTTP 403, acrescenta uma orientação específica. No modo interativo, `main()` também captura falhas na consulta das resoluções e volta a pedir um link.

O programa precisa de acesso à internet. A consulta bem-sucedida dos formatos não testa toda a transferência: o download pode falhar depois.

## 8. Como o `.exe` é criado

[`build.ps1`](build.ps1) procura o Python do ambiente virtual `.venv`, baixa o Node.js v24.22.1 LTS para `.tools/`, confere seu SHA-256 e chama o PyInstaller com `--onefile --console`.

O comando inclui `yt_dlp`, `yt_dlp_ejs`, `imageio_ffmpeg` e `node.exe` no pacote. O PyInstaller também inclui o interpretador Python necessário ao aplicativo. Assim, quem recebe `dist\BaixarVideos.exe` não precisa instalar Python, Node.js ou FFmpeg separadamente.

| Pasta ou arquivo | Papel |
| --- | --- |
| `main.py` | Código do programa. |
| `.venv/` | Ambiente Python usado para desenvolver e compilar. |
| `build/` | Arquivos intermediários do PyInstaller; podem ser recriados. |
| `dist/BaixarVideos.exe` | Executável final para distribuir no Windows. |
| `build/BaixarVideos.spec` | Receita do PyInstaller gerada durante a compilação. |

Na execução de um pacote `--onefile`, o PyInstaller extrai os componentes necessários para uma pasta temporária e inicia o programa. A pasta `build/` pertence à **compilação**; ela não precisa acompanhar o `.exe` em outro computador.

## 9. Exercício para acompanhar a execução

Abra [`main.py`](main.py) e siga esta sequência:

1. Ache `if __name__ == "__main__"` e vá para `main()`.
2. Veja onde `main()` recebe o link e chama `available_resolutions(url)`.
3. Em `available_resolutions()`, encontre `download=False` e a criação da lista `heights`.
4. Volte a `main()` e siga a chamada a `choose_resolution(heights)`.
5. Encontre a altura escolhida sendo passada a `download_video()`.
6. Em `download_video()`, identifique `options` e depois `downloader.download([url])`.

Se você consegue explicar o que cada uma dessas seis etapas recebe e devolve, já entendeu o caminho principal do programa.

### Mini glossário

- **Função:** bloco de código que executa uma tarefa, como `downloads_folder()`.
- **Argumento:** informação entregue a uma função, como `url` ou `height`.
- **Retorno:** valor que a função devolve; `choose_resolution()` devolve uma altura ou `None`.
- **Biblioteca:** código pronto usado pelo projeto, como `yt-dlp`.
- **Fluxo:** parte de mídia oferecida pelo serviço; vídeo e áudio podem ser fluxos distintos.
- **Empacotar:** juntar o código e suas dependências em um executável.
