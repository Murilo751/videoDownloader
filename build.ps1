$ErrorActionPreference = 'Stop'

$python = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $python)) {
    throw 'Ambiente virtual ausente. Instale requirements.txt e requirements-build.txt primeiro.'
}

$node = (Get-Command node.exe -ErrorAction Stop).Source

Push-Location $PSScriptRoot
try {
    & $python -m PyInstaller --noconfirm --clean --onefile --console `
        --name BaixarVideos `
        --collect-all yt_dlp `
        --collect-all yt_dlp_ejs `
        --collect-all imageio_ffmpeg `
        --exclude-module Cryptodome `
        --exclude-module Crypto `
        --add-binary "$node;." `
        main.py
    if ($LASTEXITCODE -ne 0) {
        throw 'Falha ao criar o executável.'
    }
    Write-Host "Executável criado em: $(Join-Path $PSScriptRoot 'dist\BaixarVideos.exe')"
}
finally {
    Pop-Location
}
