# Script para iniciar CuentaCuentos AI - Arquitectura API-First
# Ejecuta backend y frontend en terminales separados

Write-Host "🌟 Iniciando CuentaCuentos AI - Arquitectura API-First" -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host ""

# Verificar estructura del proyecto
if (!(Test-Path "backend\main.py")) {
    Write-Host "❌ Error: No se encuentra backend\main.py" -ForegroundColor Red
    Write-Host "Ejecuta este script desde la raíz del proyecto CuentaCuentos" -ForegroundColor Yellow
    exit 1
}

if (!(Test-Path "frontend\index.html")) {
    Write-Host "❌ Error: No se encuentra frontend\index.html" -ForegroundColor Red
    exit 1
}

if (!(Test-Path "backend\.venv")) {
    Write-Host "❌ Error: No se encuentra el entorno virtual en backend\.venv" -ForegroundColor Red
    Write-Host "El entorno virtual debe estar en backend\.venv" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Estructura del proyecto verificada" -ForegroundColor Green
Write-Host ""

# Función para iniciar backend
Write-Host "🔧 Iniciando Backend API..." -ForegroundColor Yellow
Write-Host "Puerto: 8000 | Docs: http://localhost:8000/docs" -ForegroundColor Gray

# Crear comando para backend en nueva terminal
$backendCommand = @"
cd '$PWD\backend'
Write-Host '🔧 Activando entorno virtual...' -ForegroundColor Yellow
& '.\\.venv\\Scripts\\Activate.ps1'
Write-Host '✅ Entorno virtual activado' -ForegroundColor Green

Write-Host '📦 Verificando dependencias...' -ForegroundColor Yellow
pip install --quiet uvicorn fastapi

Write-Host '🚀 Iniciando uvicorn...' -ForegroundColor Green
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
"@

# Función para iniciar frontend  
Write-Host "🌐 Iniciando Frontend Web..." -ForegroundColor Yellow
Write-Host "Puerto: 3000 | App: http://localhost:3000" -ForegroundColor Gray

$frontendCommand = @"
cd '$PWD\frontend'
Write-Host '🌐 Frontend iniciado en puerto 3000' -ForegroundColor Green
python -m http.server 3000
"@

# Iniciar backend en terminal separada
Write-Host ""
Write-Host "Abriendo terminal para Backend API..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCommand

# Esperar un momento para que el backend inicie
Start-Sleep -Seconds 3

# Iniciar frontend en terminal separada
Write-Host "Abriendo terminal para Frontend Web..." -ForegroundColor Cyan  
Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendCommand

# Esperar un momento más
Start-Sleep -Seconds 2

Write-Host ""
Write-Host "🎊 ¡CuentaCuentos AI iniciado!" -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Green
Write-Host "📱 Frontend:      http://localhost:3000" -ForegroundColor White
Write-Host "🔌 Backend API:   http://localhost:8000" -ForegroundColor White  
Write-Host "📋 API Docs:      http://localhost:8000/docs" -ForegroundColor White
Write-Host "💚 Health Check:  http://localhost:8000/health" -ForegroundColor White
Write-Host ""
Write-Host "Presiona Ctrl+C en las terminales para detener los servicios" -ForegroundColor Yellow
Write-Host "===============================================" -ForegroundColor Green

# Abrir navegador automáticamente
Write-Host "🌐 Abriendo navegador..." -ForegroundColor Cyan
Start-Sleep -Seconds 3
Start-Process "http://localhost:3000"