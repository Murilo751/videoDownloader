$ErrorActionPreference = 'Stop'

$python = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $python)) {
    throw 'Ambiente virtual ausente. Instale requirements.txt e requirements-build.txt primeiro.'
}

$nodeVersion = '24.22.1'
$nodeHash = 'd702daa815eabbff763c7d3808e235cf031cf2ca70211b56847bc72f51e240e5'
$nodeFolder = Join-Path $PSScriptRoot ".tools\node-v$nodeVersion"
$node = Join-Path $nodeFolder 'node.exe'
New-Item -ItemType Directory -Path $nodeFolder -Force | Out-Null

if (-not (Test-Path -LiteralPath $node) -or
    (Get-FileHash -LiteralPath $node -Algorithm SHA256).Hash -ne $nodeHash) {
    $download = Join-Path $nodeFolder 'node.exe.download'
    try {
        Write-Host "Baixando Node.js v$nodeVersion da distribuição oficial..."
        Invoke-WebRequest "https://nodejs.org/dist/v$nodeVersion/win-x64/node.exe" -OutFile $download
        if ((Get-FileHash -LiteralPath $download -Algorithm SHA256).Hash -ne $nodeHash) {
            throw 'O SHA-256 do Node.js não confere com o publicado pela equipe do Node.js.'
        }
        Move-Item -LiteralPath $download -Destination $node -Force
    }
    finally {
        if (Test-Path -LiteralPath $download) {
            Remove-Item -LiteralPath $download
        }
    }
}
if ((& $node --version) -ne "v$nodeVersion") {
    throw "O binário do Node.js não é a versão v$nodeVersion."
}

Push-Location $PSScriptRoot
try {
    & $python -m PyInstaller --noconfirm --clean --onefile --console `
        --name BaixarVideos `
        --specpath build `
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
