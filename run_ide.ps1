$ErrorActionPreference = 'Stop'

if (-not (Test-Path '.venv311\Scripts\python.exe')) {
    Write-Host 'No existe .venv311. Ejecutando setup_env.ps1...'
    .\setup_env.ps1
}

.\.venv311\Scripts\python.exe -m ide.main
