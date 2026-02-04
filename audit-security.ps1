# Script de Auditoría de Seguridad para CuentaCuentos AI
# Ejecuta este script ANTES de hacer git push

Write-Host "`n🔒 AUDITORÍA DE SEGURIDAD - CuentaCuentos AI" -ForegroundColor Cyan
Write-Host "============================================`n" -ForegroundColor Cyan

$errorsFound = 0
$warningsFound = 0

# 1. Verificar que .gitignore existe
Write-Host "📋 Verificando .gitignore..." -ForegroundColor Yellow
if (Test-Path ".gitignore") {
    Write-Host "   ✅ .gitignore existe" -ForegroundColor Green
} else {
    Write-Host "   ❌ .gitignore NO EXISTE - CRÍTICO" -ForegroundColor Red
    $errorsFound++
}

# 2. Verificar que .env está ignorado
Write-Host "`n🔑 Verificando archivos .env..." -ForegroundColor Yellow
if (Test-Path "backend/.env") {
    $isIgnored = git check-ignore "backend/.env" 2>$null
    if ($isIgnored) {
        Write-Host "   ✅ backend/.env existe y está IGNORADO por git" -ForegroundColor Green
    } else {
        Write-Host "   ❌ backend/.env existe pero NO está ignorado - CRÍTICO" -ForegroundColor Red
        $errorsFound++
    }
} else {
    Write-Host "   ⚠️  backend/.env no existe (necesario para ejecutar la app)" -ForegroundColor Yellow
    $warningsFound++
}

# 3. Verificar que .env NO está en staging
Write-Host "`n📦 Verificando staging area..." -ForegroundColor Yellow
$stagedEnv = git diff --cached --name-only | Select-String "\.env$" | Where-Object { $_ -notmatch "example" }
if ($stagedEnv) {
    Write-Host "   ❌ ARCHIVO .env DETECTADO EN STAGING:" -ForegroundColor Red
    $stagedEnv | ForEach-Object { Write-Host "      - $_" -ForegroundColor Red }
    Write-Host "   EJECUTA: git reset HEAD backend/.env" -ForegroundColor Yellow
    $errorsFound++
} else {
    Write-Host "   ✅ No hay archivos .env en staging" -ForegroundColor Green
}

# 4. Verificar bases de datos
Write-Host "`n💾 Verificando archivos de base de datos..." -ForegroundColor Yellow
$stagedDb = git diff --cached --name-only | Select-String "\.db$|\.sqlite$"
if ($stagedDb) {
    Write-Host "   ⚠️  ARCHIVOS DE BASE DE DATOS EN STAGING:" -ForegroundColor Yellow
    $stagedDb | ForEach-Object { Write-Host "      - $_" -ForegroundColor Yellow }
    $warningsFound++
} else {
    Write-Host "   ✅ No hay archivos .db en staging" -ForegroundColor Green
}

# 5. Buscar claves de API en archivos staged
Write-Host "`n🔍 Buscando claves expuestas en código..." -ForegroundColor Yellow
$apiKeyPattern = "AIzaSy[A-Za-z0-9_-]{33}"
$stagedFiles = git diff --cached --name-only
$keysFound = $false

foreach ($file in $stagedFiles) {
    if ($file -notmatch "\.env" -and (Test-Path $file)) {
        $content = Get-Content $file -Raw -ErrorAction SilentlyContinue
        if ($content -match $apiKeyPattern) {
            Write-Host "   ❌ CLAVE DE API ENCONTRADA EN: $file" -ForegroundColor Red
            $keysFound = $true
            $errorsFound++
        }
    }
}

if (-not $keysFound) {
    Write-Host "   ✅ No se encontraron claves de API expuestas" -ForegroundColor Green
}

# 6. Verificar entorno virtual
Write-Host "`n🐍 Verificando entorno virtual..." -ForegroundColor Yellow
$stagedVenv = git diff --cached --name-only | Select-String "\.venv|venv"
if ($stagedVenv) {
    Write-Host "   ⚠️  ARCHIVOS DE ENTORNO VIRTUAL EN STAGING:" -ForegroundColor Yellow
    $stagedVenv | ForEach-Object { Write-Host "      - $_" -ForegroundColor Yellow }
    $warningsFound++
} else {
    Write-Host "   ✅ Entorno virtual no está en staging" -ForegroundColor Green
}

# 7. Verificar archivos grandes
Write-Host "`n📏 Verificando tamaño de archivos..." -ForegroundColor Yellow
$largeFiles = git diff --cached --name-only | ForEach-Object {
    if (Test-Path $_) {
        $size = (Get-Item $_).Length / 1MB
        if ($size -gt 1) {
            [PSCustomObject]@{
                File = $_
                SizeMB = [math]::Round($size, 2)
            }
        }
    }
}

if ($largeFiles) {
    Write-Host "   ⚠️  ARCHIVOS GRANDES DETECTADOS:" -ForegroundColor Yellow
    $largeFiles | ForEach-Object { Write-Host "      - $($_.File) ($($_.SizeMB) MB)" -ForegroundColor Yellow }
    $warningsFound++
} else {
    Write-Host "   ✅ No hay archivos inusualmente grandes" -ForegroundColor Green
}

# 8. Verificar .env.example
Write-Host "`n📄 Verificando .env.example..." -ForegroundColor Yellow
if (Test-Path "backend/.env.example") {
    $exampleContent = Get-Content "backend/.env.example" -Raw
    if ($exampleContent -match $apiKeyPattern) {
        Write-Host "   ❌ .env.example contiene una API key real - CRÍTICO" -ForegroundColor Red
        $errorsFound++
    } else {
        Write-Host "   ✅ .env.example no contiene claves reales" -ForegroundColor Green
    }
} else {
    Write-Host "   ⚠️  backend/.env.example no existe" -ForegroundColor Yellow
    $warningsFound++
}

# 9. Lista de archivos que se van a subir
Write-Host "`n📋 Archivos que se subirán a GitHub:" -ForegroundColor Yellow
$stagedCount = (git diff --cached --name-only | Measure-Object).Count
if ($stagedCount -eq 0) {
    Write-Host "   ⚠️  No hay archivos en staging area" -ForegroundColor Yellow
} else {
    Write-Host "   Total: $stagedCount archivos" -ForegroundColor Cyan
    git diff --cached --name-only | ForEach-Object { Write-Host "   - $_" -ForegroundColor Gray }
}

# RESUMEN FINAL
Write-Host "`n" -NoNewline
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "📊 RESUMEN DE AUDITORÍA" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan

if ($errorsFound -eq 0 -and $warningsFound -eq 0) {
    Write-Host "`n✅ TODO CORRECTO - SEGURO PARA GITHUB" -ForegroundColor Green
    Write-Host "`nPuedes proceder con:" -ForegroundColor Green
    Write-Host "   git commit -m 'tu mensaje'" -ForegroundColor Cyan
    Write-Host "   git push origin main" -ForegroundColor Cyan
    exit 0
} elseif ($errorsFound -gt 0) {
    Write-Host "`n❌ ERRORES CRÍTICOS ENCONTRADOS: $errorsFound" -ForegroundColor Red
    Write-Host "`n⚠️  NO HAGAS PUSH HASTA CORREGIR LOS ERRORES" -ForegroundColor Red
    Write-Host "`nAcciones recomendadas:" -ForegroundColor Yellow
    Write-Host "   1. Revisa los errores marcados arriba" -ForegroundColor Yellow
    Write-Host "   2. Ejecuta: git reset HEAD <archivo>" -ForegroundColor Yellow
    Write-Host "   3. Vuelve a ejecutar este script" -ForegroundColor Yellow
    exit 1
} else {
    Write-Host "`n⚠️  ADVERTENCIAS ENCONTRADAS: $warningsFound" -ForegroundColor Yellow
    Write-Host "`nRevisa las advertencias antes de continuar" -ForegroundColor Yellow
    Write-Host "`nSi todo está correcto, puedes proceder con:" -ForegroundColor Green
    Write-Host "   git commit -m 'tu mensaje'" -ForegroundColor Cyan
    Write-Host "   git push origin main" -ForegroundColor Cyan
    exit 0
}
