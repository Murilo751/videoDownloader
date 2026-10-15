# Baixador de vídeos em MP4

Para entender o funcionamento do programa e estudar o código, leia o [guia passo a passo](GUIA_DO_CODIGO.md).

## Para quem recebeu o programa

1. No Windows, abra `BaixarVideos.exe` com dois cliques. Uma janela de terminal abrirá com o logo **videoDownloader**.
2. Cole o link de um vídeo do YouTube e pressione Enter.
3. Use as setas esquerda/direita para escolher a resolução entre **Mín.** e **Máx.**; confirme com Enter.
4. Aguarde o MP4 na pasta **Downloads** do seu computador.
5. Cole outro link para baixar mais vídeos ou pressione Enter sem digitar nada para sair.

O seletor mostra as resoluções MP4 disponíveis para cada vídeo. Se não houver vídeo MP4 com áudio, o programa mostra um erro. É preciso ter acesso à internet. Use apenas para vídeos que você tem permissão para baixar.

## Para executar pelo Python

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe main.py
```

O uso pelo Python requer [Node.js 22 ou mais recente](https://nodejs.org/en/download). Para baixar diretamente um link ou usar outra pasta:

```powershell
.venv\Scripts\python.exe main.py "https://youtu.be/ID_DO_VIDEO"
.venv\Scripts\python.exe main.py "https://youtu.be/ID_DO_VIDEO" --saida "C:\Videos"
```

`--verificar` consulta os formatos disponíveis, mas não testa a transferência completa.

## Para gerar o executável

No computador de compilação, com Python e Node.js instalados:

```powershell
.venv\Scripts\python.exe -m pip install -r requirements-build.txt
.\build.ps1
```

O arquivo final fica em `dist\BaixarVideos.exe`. Ele inclui Python, FFmpeg e Node.js; quem receber o executável não precisa instalá-los.
