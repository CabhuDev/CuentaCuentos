# 🔒 Seguridad y Mejores Prácticas

## ⚠️ IMPORTANTE: Antes de Subir a GitHub

Este documento contiene información crítica de seguridad para el proyecto CuentaCuentos AI.

## 🛡️ Archivos Sensibles

### Archivos que NUNCA deben subirse a GitHub:

1. **`backend/.env`** - Contiene API keys (Gemini, ElevenLabs, Brevo) y SECRET_KEY
2. **`backend/*.db`** - Bases de datos SQLite con datos de producción y tokens de sesión
3. **`backend/.venv/`** - Entorno virtual de Python
4. **`backend/data/*.json`** - Pueden contener datos sensibles de desarrollo
5. **`backend/__pycache__/`** - Archivos compilados de Python
6. **Cualquier archivo con contraseñas o tokens** - Logs, dumps, respaldos

### ✅ Verificación antes de commit

Ejecuta estos comandos antes de hacer `git push`:

```bash
# 1. Verifica que .env NO esté en staging
git status | Select-String ".env"

# 2. Verifica que .gitignore funciona correctamente
git check-ignore -v backend/.env backend/*.db backend/.venv

# 3. Lista solo archivos que SERÁN commiteados
git diff --cached --name-only

# 4. Busca claves expuestas en archivos staged
git diff --cached | Select-String "AIzaSy"
```

## 🔑 Gestión de API Keys y Secretos

### Google Gemini API Key

**¿Dónde está mi clave?**
- ✅ `backend/.env` (ignorado por git)
- ✅ `backend/.env.example` (plantilla SIN clave real)

**¿Dónde NO debe estar?**
- ❌ En archivos Python (.py)
- ❌ En archivos de documentación (.md)
- ❌ En archivos JSON de configuración
- ❌ En commits de git

### ElevenLabs API Key (Text-to-Speech)

**Protección:**
- ✅ Solo en `backend/.env`
- ❌ Nunca en código fuente
- ❌ Nunca en logs del servidor

**Obtener clave:** [ElevenLabs Dashboard](https://elevenlabs.io/)

### Brevo API Key (Servicio de Email)

**Protección:**
- ✅ Solo en `backend/.env`
- ❌ Nunca en código fuente
- ✅ Plan gratuito: 300 emails/día

**Obtener clave:** [Brevo API Keys](https://app.brevo.com/settings/keys/api)

**Permisos necesarios:**
- ✅ Send emails
- ❌ No necesita acceso de lectura

### SECRET_KEY (JWT Authentication)

**Generación segura:**
```bash
# Genera una clave aleatoria de 32 bytes
openssl rand -hex 32

# O en PowerShell
[Convert]::ToBase64String((1..32 | ForEach-Object { Get-Random -Minimum 0 -Maximum 256 }))
```

**Requisitos:**
- Mínimo 32 caracteres
- Caracteres aleatorios
- Única por entorno (desarrollo, producción)
- ❌ NUNCA reutilices la del `.env.example`

**Impacto si se expone:**
- ⚠️ Atacantes pueden generar tokens de sesión válidos
- ⚠️ Puede comprometer todas las cuentas de usuario
- 🔄 **Acción:** Regenerar inmediatamente y cerrar todas las sesiones activas

### Tokens de Reset de Contraseña

**Características de seguridad:**
- ✅ Generados con `secrets.token_urlsafe(32)` (256 bits de entropía)
- ✅ Expiran en 1 hora
- ✅ Un solo uso (marcados como usados en BD)
- ✅ Almacenados en base de datos, no en archivos

**Buenas prácticas:**
- ❌ No logs de tokens en producción
- ✅ HTTPS obligatorio para enlaces de reset
- ✅ Limpieza periódica de tokens expirados

### Si expones accidentalmente una clave:

**Para API Keys (Gemini, ElevenLabs, Brevo):**

1. **Regenera INMEDIATAMENTE** la API key en el dashboard correspondiente:
   - Gemini: [Google AI Studio](https://aistudio.google.com/app/apikey)
   - ElevenLabs: [Dashboard](https://elevenlabs.io/)
   - Brevo: [API Keys](https://app.brevo.com/settings/keys/api)

2. Actualiza tu `backend/.env` con la nueva clave

3. Si ya hiciste commit:
   ```bash
   # Reescribe la historia de git (PELIGROSO - úsalo con cuidado)
   git filter-branch --force --index-filter \
     "git rm --cached --ignore-unmatch backend/.env" \
     --prune-empty --tag-name-filter cat -- --all
   
   # Fuerza el push (si ya subiste a GitHub)
   git push origin --force --all
   ```

**Para SECRET_KEY:**

1. **Genera nueva SECRET_KEY** inmediatamente
2. **Invalida todas las sesiones activas** (cerrar sesión de todos los usuarios)
3. **Notifica a usuarios** sobre el cambio de seguridad
4. **Revisa logs** para detectar accesos no autorizados

## 📋 Checklist de Seguridad

Antes de hacer tu primer push a GitHub:

- [ ] Archivo `.gitignore` actualizado y funcionando
- [ ] Archivo `backend/.env` existe pero está ignorado por git
- [ ] Archivo `backend/.env.example` NO contiene claves reales
- [ ] No hay claves hardcodeadas en archivos `.py`
- [ ] No hay claves en documentación `.md`
- [ ] Base de datos `.db` está ignorada
- [ ] Entorno virtual `.venv` está ignorado
- [ ] Ejecutaste `git status` y verificaste que solo suben archivos seguros

## 🔍 Auditoría de Seguridad

### Buscar claves expuestas en todo el proyecto:

```powershell
# Buscar patrones de Google API Keys
Get-ChildItem -Path . -Recurse -File | 
  Select-String "AIzaSy[A-Za-z0-9_-]{33}" | 
  Where-Object { $_.Path -notlike "*\.env" -and $_.Path -notlike "*\.venv*" }

# Buscar patrones de ElevenLabs API Keys
Get-ChildItem -Path . -Recurse -File | 
  Select-String "[a-f0-9]{32}" |
  Where-Object { $_.Path -notlike "*\.env" }

# Buscar patrones de Brevo API Keys
Get-ChildItem -Path . -Recurse -File | 
  Select-String "xkeysib-[a-zA-Z0-9-]+" |
  Where-Object { $_.Path -notlike "*\.env" }

# Buscar patrones de SECRET_KEY
Get-ChildItem -Path . -Recurse -File | 
  Select-String "SECRET_KEY\s*=\s*['\"][^'\"]{32,}['\"]" |
  Where-Object { $_.Path -notlike "*\.env" }

# Buscar patrones de contraseñas
Get-ChildItem -Path . -Recurse -File | 
  Select-String -Pattern "password\s*=\s*['\"][^'\"]+['\"]" |
  Where-Object { $_.Path -notlike "*\.env*" }
```

### Verificar archivos que están siendo trackeados:

```bash
# Ver TODOS los archivos en el repositorio
git ls-files

# Buscar archivos .env específicamente
git ls-files | Select-String "\.env$"

# Verificar archivos grandes (pueden ser dumps de DB)
git ls-files | ForEach-Object { 
  if (Test-Path $_) { 
    [PSCustomObject]@{
      File = $_
      Size = (Get-Item $_).Length / 1KB
    }
  }
} | Where-Object Size -gt 100 | Sort-Object Size -Descending
```

## 🌐 Configuración para GitHub

### README público seguro

Cuando documentes tu proyecto:

```markdown
## Configuración

1. Clona el repositorio
2. Copia `backend/.env.example` a `backend/.env`
3. Obtén tu Google Gemini API key en https://aistudio.google.com/app/apikey
4. Edita `backend/.env` y añade tu clave:
   ```
   GEMINI_API_KEY=tu_clave_aqui
   ```
5. Nunca subas el archivo .env a GitHub
```

### GitHub Secrets (para CI/CD)

Si usas GitHub Actions, configura secrets:

1. Ve a Settings → Secrets and variables → Actions
2. Añade: `GEMINI_API_KEY` con tu clave real
3. Úsalo en workflows: `${{ secrets.GEMINI_API_KEY }}`

## 🚨 Señales de Alerta

**Ejecuta esto antes de cada push:**

```bash
# Si este comando devuelve resultados, ¡DETENTE!
git diff --cached | Select-String -Pattern "AIzaSy", "password", "secret", "token"
```

## 📞 ¿Qué hacer si expones una clave?

1. **NO ENTRES EN PÁNICO** pero actúa rápido
2. **Revoca/regenera** la clave inmediatamente
3. **Reescribe el historial** de git (ver sección arriba)
4. **Notifica** si es un proyecto compartido
5. **Revisa logs** de Google Cloud para ver si alguien usó la clave

## ✅ Estado de Seguridad Actual

### Protecciones Activas:

- ✅ `.gitignore` configurado correctamente
- ✅ `backend/.env` NO está en staging
- ✅ `backend/.env.example` sin claves reales
- ✅ Bases de datos ignoradas
- ✅ Entorno virtual ignorado
- ✅ No hay claves hardcodeadas en código Python
- ✅ Documentación actualizada con instrucciones seguras
- ✅ JWT con SECRET_KEY en entorno
- ✅ Hashing de contraseñas con Bcrypt
- ✅ Tokens de reset seguros con expiración
- ✅ Rate limiting recomendado en producción

### Configuración de Seguridad para Contraseñas:

- ✅ Hash con Bcrypt (coste adaptativo)
- ✅ Tokens de reset de un solo uso
- ✅ Expiración automática de tokens (1 hora)
- ✅ Mensajes ambiguos (no revela si email existe)
- ✅ Verificación de contraseña actual para cambios
- ✅ Emails de notificación por cambios de seguridad
- ⚠️ Requiere HTTPS en producción
- ⚠️ Recomienda rate limiting en endpoints de auth

### Archivos Seguros para GitHub:

Todos los archivos actualmente en staging (`git status`) son seguros:
- Código fuente Python (.py)
- Documentación (.md)
- Configuración de ejemplo (.env.example)
- Archivos frontend (HTML, CSS, JS)
- Scripts de utilidad (.ps1)

---

**Última auditoría:** 9 de febrero de 2026

## 📚 Referencias Adicionales

- [Guía de Reset de Contraseña](guides/password-reset.md)
- [Documentación de Brevo](https://developers.brevo.com/)
- [OWASP Password Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)
- [JWT Best Practices](https://tools.ietf.org/html/rfc8725)
**Estado:** ✅ SEGURO PARA GITHUB
