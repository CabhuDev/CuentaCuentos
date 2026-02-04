# Script para configurar SQLite como base de datos de desarrollo
# Ejecutar desde la raíz del proyecto: .\configurar-sqlite.ps1

Write-Host "🔧 Configurando CuentaCuentos AI con SQLite" -ForegroundColor Cyan
Write-Host "===========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar que estamos en la raíz del proyecto
if (!(Test-Path "backend\config.py")) {
    Write-Host "❌ Error: Ejecuta este script desde la raíz del proyecto CuentaCuentos" -ForegroundColor Red
    exit 1
}

# Crear archivo .env si no existe
$envPath = "backend\.env"
if (!(Test-Path $envPath)) {
    Write-Host "📝 Creando archivo .env..." -ForegroundColor Yellow
    
    # Solicitar API key de Gemini
    Write-Host ""
    Write-Host "Para usar CuentaCuentos AI necesitas una API key de Google Gemini" -ForegroundColor White
    Write-Host "Obtén tu clave gratis en: https://aistudio.google.com/app/apikey" -ForegroundColor Cyan
    Write-Host ""
    $apiKey = Read-Host "Ingresa tu GEMINI_API_KEY (o presiona Enter para configurar después)"
    
    if ([string]::IsNullOrWhiteSpace($apiKey)) {
        $apiKey = "tu_api_key_aqui"
        Write-Host "⚠️  Recuerda configurar tu API key en backend\.env antes de usar la app" -ForegroundColor Yellow
    }
    
    # Crear archivo .env con SQLite
    @"
# API Key de Google Gemini
GEMINI_API_KEY=$apiKey

# Base de Datos SQLite (para desarrollo sin PostgreSQL)
DATABASE_URL=sqlite:///./cuentacuentos.db
"@ | Out-File -FilePath $envPath -Encoding utf8
    
    Write-Host "✅ Archivo .env creado" -ForegroundColor Green
} else {
    Write-Host "✅ Archivo .env ya existe" -ForegroundColor Green
    
    # Verificar si tiene DATABASE_URL configurado
    $envContent = Get-Content $envPath -Raw
    if ($envContent -notmatch "DATABASE_URL") {
        Write-Host "📝 Agregando configuración de SQLite al .env existente..." -ForegroundColor Yellow
        Add-Content -Path $envPath -Value "`n# Base de Datos SQLite (para desarrollo sin PostgreSQL)`nDATABASE_URL=sqlite:///./cuentacuentos.db"
        Write-Host "✅ DATABASE_URL agregado" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "🔄 Actualizando config.py para usar database_sqlite..." -ForegroundColor Yellow

# Leer config.py
$configPath = "backend\config.py"
$configContent = Get-Content $configPath -Raw

# Reemplazar la línea de DATABASE_URL si no está usando el .env correctamente
if ($configContent -notmatch 'os\.getenv\("DATABASE_URL", "sqlite:') {
    $configContent = $configContent -replace 'DATABASE_URL = os\.getenv\([^)]+\)', 'DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./cuentacuentos.db")'
    $configContent | Out-File -FilePath $configPath -Encoding utf8 -NoNewline
    Write-Host "✅ config.py actualizado" -ForegroundColor Green
}

Write-Host ""
Write-Host "🗄️  Inicializando base de datos SQLite..." -ForegroundColor Yellow

# Activar entorno virtual e inicializar base de datos
$initScript = @"
cd backend
& '.\.venv\Scripts\Activate.ps1'
python -c "from models.database_sqlite import init_db; init_db()"
"@

Invoke-Expression $initScript

Write-Host ""
Write-Host "✅ ¡Configuración completada!" -ForegroundColor Green
Write-Host ""
Write-Host "Ahora puedes iniciar la aplicación con: .\iniciar.ps1" -ForegroundColor Cyan
Write-Host ""
Write-Host "📝 Nota: SQLite es ideal para desarrollo local." -ForegroundColor Gray
Write-Host "    Para producción, configura PostgreSQL con pgvector en el .env" -ForegroundColor Gray
