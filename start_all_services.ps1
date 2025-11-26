# ============================================================
# Script : start_all_services.ps1
# Objectif : Démarrer tous les microservices FastAPI (Auth, Sports, Reco, Chat)
# ============================================================

$ErrorActionPreference = "Stop"

# 1) Racine = dossier où se trouve CE script
$RACINE = Split-Path -Parent $MyInvocation.MyCommand.Path

# 2) Python (venv si présent, sinon python global)
$PY_VENV = Join-Path $RACINE "venv\Scripts\python.exe"
if (Test-Path $PY_VENV) {
  $PYTHON = $PY_VENV
  Write-Host "Python (venv) détecté : $PYTHON" -ForegroundColor DarkGray
} else {
  $PYTHON = "python"
  Write-Host "Aucun python du venv trouvé, utilisation de : $PYTHON" -ForegroundColor Yellow
}

# 3) Définition des microservices
$SERVICES = @(
  @{ Nom="authentification"; Dossier="auth_service_fastapi"; Port=8001; Module="app.main" },
  @{ Nom="sports";           Dossier="sports_service_fastapi"; Port=8002; Module="app.main" },
  @{ Nom="recommandation";   Dossier="reco_service_fastapi";   Port=8003; Module="app.main" },
  @{ Nom="chatbot";          Dossier="chatbot_service_fastapi";Port=8010; Module="app.main" }
)

Write-Host "==========================================="
Write-Host "DÉMARRAGE DES MICROSERVICES FASTAPI" -ForegroundColor Green
Write-Host "Racine du projet : $RACINE" -ForegroundColor DarkGray
Write-Host "==========================================="

foreach ($svc in $SERVICES) {
  $CheminService = Join-Path $RACINE ("services\" + $svc.Dossier)

  if (!(Test-Path $CheminService)) {
    Write-Host "Erreur : dossier introuvable $CheminService" -ForegroundColor Red
    continue
  }

  $commande = @"
cd "$CheminService"
& "$PYTHON" -m $($svc.Module)
"@

  Start-Process powershell -ArgumentList "-NoExit","-Command",$commande | Out-Null
  Write-Host ("Service {0} lancé (port {1})" -f $svc.Nom, $svc.Port) -ForegroundColor Cyan
}

Write-Host "-------------------------------------------"
Write-Host "Tous les services ont été lancés."
Write-Host "Tests rapides :"
Write-Host "  http://127.0.0.1:8001/auth/health (Auth)"
Write-Host "  http://127.0.0.1:8002/sports        (Sports)"
Write-Host "  http://127.0.0.1:8003/reco/health   (Reco -> si defines endpoint)"
Write-Host "  http://127.0.0.1:8010/chat/health   (Chat)"
Write-Host "-------------------------------------------"
