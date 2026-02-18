$ErrorActionPreference = 'Stop'

Write-Host 'Configurando entorno para Skuld IDE...'

$hasPy311 = $false
try {
    py -3.11 --version | Out-Null
    $hasPy311 = $true
}
catch {
    $hasPy311 = $false
}

if (-not $hasPy311) {
    Write-Error "No se encontro Python 3.11. Instala Python 3.11 y vuelve a ejecutar este script."
}

if (Test-Path '.venv311\Scripts\python.exe') {
    $venvVersion = & .\.venv311\Scripts\python.exe -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
    if ($venvVersion -ne '3.11') {
        Write-Host "Se encontro .venv311 con Python $venvVersion. Recreando con 3.11..."
        Remove-Item -Recurse -Force .venv311
    }
}

if (-not (Test-Path '.venv311')) {
    Write-Host 'Creando entorno virtual .venv311 con Python 3.11...'
    py -3.11 -m venv .venv311
}

Write-Host 'Instalando dependencias del proyecto...'
.\.venv311\Scripts\python.exe -m pip install --upgrade pip
.\.venv311\Scripts\python.exe -m pip install -r requirements.txt

Write-Host 'Entorno listo. Ejecuta: .\\run_ide.ps1'
