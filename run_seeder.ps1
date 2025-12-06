# Script PowerShell pour executer le seeder facilement
# Utilise automatiquement le Python de l'environnement virtuel si disponible

$VENV_PYTHON = ".\venv\Scripts\python.exe"
$PYTHON = "python"

# Verifier si l'environnement virtuel existe
if (Test-Path $VENV_PYTHON) {
    Write-Host "Utilisation de l'environnement virtuel Python" -ForegroundColor Green
    $PYTHON_CMD = $VENV_PYTHON
} else {
    Write-Host "Environnement virtuel non trouve, utilisation de Python global" -ForegroundColor Yellow
    $PYTHON_CMD = $PYTHON
}

# Verifier les arguments
if ($args.Count -eq 0) {
    Write-Host ""
    Write-Host "Script de Seeding SportConnectIA" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Usage :"
    Write-Host "  .\run_seeder.ps1 --all              # Peuple toutes les bases"
    Write-Host "  .\run_seeder.ps1 --all --clear      # Nettoie et peuple toutes les bases"
    Write-Host "  .\run_seeder.ps1 --auth             # Seulement Auth Service"
    Write-Host "  .\run_seeder.ps1 --chatbot          # Seulement Chatbot Service"
    Write-Host "  .\run_seeder.ps1 --tracking         # Seulement Tracking/Metrics (MongoDB)"
    Write-Host "  .\run_seeder.ps1 --mongodb          # Seulement MongoDB (users et recommendations)"
    Write-Host ""
    exit 0
}

# Executer le seeder
Write-Host ""
Write-Host "Execution du seeder..." -ForegroundColor Cyan
Write-Host ""
& $PYTHON_CMD seed\seeder.py $args

# Verifier le code de sortie
if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "Seeding termine avec succes !" -ForegroundColor Green
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "Erreur lors de l'execution du seeding (code : $LASTEXITCODE)" -ForegroundColor Red
    Write-Host ""
    exit $LASTEXITCODE
}
