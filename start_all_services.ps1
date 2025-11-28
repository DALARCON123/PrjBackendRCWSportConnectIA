# ============================================================
# Script : start_all_services.ps1
# Objectif : Démarrer tous les microservices FastAPI
#            (Auth, Sports, Reco, Chatbot) en un seul clic
# Projet  : PrjBackendRCWSportConnectIA
# ============================================================

$ErrorActionPreference = "Stop"

# 1) Racine = dossier où se trouve CE script (.ps1)
$PROJECT_ROOT = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "===========================================" -ForegroundColor Green
Write-Host " DÉMARRAGE DES MICROSERVICES FASTAPI"       -ForegroundColor Green
Write-Host " Racine du projet : $PROJECT_ROOT"          -ForegroundColor DarkGray
Write-Host "===========================================" -ForegroundColor Green

# 2) Python dans le venv
$PYTHON_EXE = Join-Path $PROJECT_ROOT "venv\Scripts\python.exe"
if (Test-Path $PYTHON_EXE) {
    Write-Host "Python du venv détecté : $PYTHON_EXE" -ForegroundColor DarkGray
} else {
    Write-Host "ATTENTION : venv introuvable, utilisation de 'python' global." -ForegroundColor Yellow
    $PYTHON_EXE = "python"
}

# 3) Définition des microservices
$SERVICES = @(
    @{
        Nom     = "authentification"
        Dossier = "auth_service_fastapi"
        Port    = 8001
        Module  = "app.main"
        TestUrl = "http://127.0.0.1:8001/auth/health"
    },
    @{
        Nom     = "sports"
        Dossier = "sports_service_fastapi"
        Port    = 8002
        Module  = "app.main"
        TestUrl = "http://127.0.0.1:8002/sports"
    },
    @{
        Nom     = "recommandation"
        Dossier = "reco_service_fastapi"
        Port    = 8004
        Module  = "app.main"
        TestUrl = "http://127.0.0.1:8004/tracking/measurements?email=test@test.com"
    },
    @{
        Nom     = "chatbot"
        Dossier = "chatbot_service_fastapi"
        Port    = 8010
        Module  = "app.main"
        TestUrl = "http://127.0.0.1:8010/chat/health"
    }
)

foreach ($svc in $SERVICES) {

    # Dossier du microservice : ...\services\<nom_service>
    $ServicePath = Join-Path $PROJECT_ROOT ("services\" + $svc.Dossier)

    if (!(Test-Path $ServicePath)) {
        Write-Host "ERREUR : Dossier introuvable : $ServicePath" -ForegroundColor Red
        continue
    }

    Write-Host ""
    Write-Host "-------------------------------------------" -ForegroundColor DarkGray
    Write-Host ("Lancement du service {0} (port {1})" -f $svc.Nom, $svc.Port) -ForegroundColor Cyan
    Write-Host ("Dossier : {0}" -f $ServicePath) -ForegroundColor DarkGray

    # Lancer directement python.exe avec -m app.main
    Start-Process `
        -FilePath $PYTHON_EXE `
        -ArgumentList "-m", $svc.Module `
        -WorkingDirectory $ServicePath
}

Write-Host ""
Write-Host "===========================================" -ForegroundColor Green
Write-Host " Tous les services ont été lancés (processus séparés)." -ForegroundColor Green
Write-Host " Tests rapides :" -ForegroundColor White
Write-Host "   Auth   : http://127.0.0.1:8001/auth/health"
Write-Host "   Sports : http://127.0.0.1:8002/sports"
Write-Host "   Reco   : http://127.0.0.1:8004/tracking/measurements?email=test@test.com"
Write-Host "   Chat   : http://127.0.0.1:8010/chat/health"
Write-Host "===========================================" -ForegroundColor Green
