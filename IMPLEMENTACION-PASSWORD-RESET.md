# Resumen de Implementación: Sistema de Reset y Cambio de Contraseña

## ✅ Implementación Completada

### 1. Base de Datos (SQLite)

**Archivos modificados:**
- `backend/models/database_sqlite.py`

**Cambios realizados:**
- ✅ Nueva tabla `password_reset_tokens` con campos:
  - `id`, `user_id`, `token`, `expires_at`, `created_at`, `used`
- ✅ Campo `email` agregado a la tabla `users`
- ✅ Funciones CRUD implementadas:
  - `get_user_by_email()`
  - `get_user_by_id()`
  - `create_password_reset_token()`
  - `get_password_reset_token()`
  - `mark_token_as_used()`
  - `delete_expired_tokens()`
  - `update_user_password()`

### 2. Servicio de Email

**Archivo creado:**
- `backend/services/email_service.py`

**Funciones implementadas:**
- ✅ `_send_template_email()` - Función genérica para templates de Brevo
- ✅ `send_welcome_email()` - Envía email de bienvenida automático
- ✅ `send_password_reset_email()` - Envía email con enlace de reset
- ✅ `send_password_changed_confirmation()` - Envía confirmación de cambio (usa template)
- ✅ `add_contact_to_list()` - Sincroniza contacto con lista de Brevo

**Integración:**
- API de Brevo con sistema de templates profesionales
- Templates configurables desde dashboard de Brevo
- Email de bienvenida automático al registrar usuario
- Sincronización automática de contactos con lista de Brevo
- Gestión de errores y timeouts
- Logging de operaciones

### 3. Schemas Pydantic

**Archivo modificado:**
- `backend/models/schemas.py`

**Nuevos schemas agregados:**
- ✅ `ForgotPasswordRequest` - Solicitud de reset
- ✅ `ResetPasswordRequest` - Reset con token
- ✅ `ChangePasswordRequest` - Cambio de contraseña autenticado
- ✅ `PasswordResetResponse` - Respuesta unificada
- ✅ Campo `email` en `UserCreate` y `User`

### 4. Servicio de Autenticación

**Archivo modificado:**
- `backend/services/auth_service.py`

**Nuevas funciones:**
- ✅ `generate_reset_token()` - Genera tokens seguros
- ✅ `create_password_reset_token()` - Crea y almacena token
- ✅ `validate_reset_token()` - Valida token y expiración
- ✅ `reset_password()` - Resetea contraseña con token
- ✅ `change_password()` - Cambia contraseña verificando la actual

### 5. Endpoints REST

**Archivo modificado:**
- `backend/routers/auth.py`

**Nuevos endpoints:**
- ✅ `POST /forgot-password` - Solicita reset de contraseña
- ✅ `POST /reset-password` - Resetea contraseña con token
- ✅ `POST /change-password` - Cambia contraseña (requiere autenticación)

### 6. Configuración

**Archivos modificados:**
- `backend/config.py` - Variables de configuración
- `backend/.env.example` - Plantilla de variables de entorno
- `backend/requirements.txt` - Dependencia `requests` agregada

**Nuevas variables de entorno:**
```env
BREVO_API_KEY=tu_api_key_de_brevo_aqui
BREVO_SENDER_EMAIL=noreply@tudominio.com
BREVO_SENDER_NAME=CuentaCuentos
FRONTEND_URL=http://localhost:3000  # Puerto de Vite en desarrollo
```

### 7. Documentación

**Archivos creados/modificados:**
- ✅ `docs/guides/password-reset.md` - Guía completa de configuración
- ✅ `README.md` - Referencias actualizadas

---

## 🔒 Características de Seguridad Implementadas

✅ **Tokens seguros**: `secrets.token_urlsafe(32)` - 32 bytes de entropía
✅ **Expiración temporal**: Tokens válidos por 1 hora
✅ **Un solo uso**: Tokens marcados como usados después de aplicarse
✅ **Hashing robusto**: Bcrypt a través de Passlib
✅ **Mensajes ambiguos**: No revela si un email existe en el sistema
✅ **Verificación de contraseña**: Requiere contraseña actual para cambios
✅ **Notificaciones**: Emails de confirmación por cambios de seguridad
✅ **Limpieza automática**: Tokens expirados eliminados periódicamente

---

## 🚀 Cómo Probar

### 1. Configurar Variables de Entorno

Edita tu archivo `.env` en `backend/`:

```env
# Obligatorio para JWT
SECRET_KEY=tu_clave_secreta_super_segura_de_64_caracteres_minimo

# Obligatorio para Brevo
BREVO_API_KEY=xkeysib-tu-api-key-aqui
BREVO_SENDER_EMAIL=noreply@tudominio.com
BREVO_SENDER_NAME=CuentaCuentos

# IDs de Templates de Brevo (opcional)
BREVO_LIST_ID=2  # ID de lista de contactos
BREVO_WELCOME_TEMPLATE_ID=2  # Template de bienvenida
BREVO_CHANGEPASS_TEMPLATE_ID=3  # Template de cambio de contraseña

# URL del frontend
FRONTEND_URL=http://localhost:3000  # Desarrollo (puerto de Vite)
# FRONTEND_URL=https://elratonsinverguencilla.es/cuentacuentos  # Producción
```

**Configuración de Templates:**
1. Crea templates en [Brevo Dashboard](https://app.brevo.com/camp/lists/template)
2. Usa estas variables en tus templates:
   - `{{ params.USERNAME }}` - Nombre de usuario
   - `{{ params.FRONTEND_URL }}` - URL del frontend
   - `{{ params.CHANGE_DATE }}` - Fecha de cambio (solo para password changed)
3. Anota los IDs de los templates y agrégalos al `.env`

**Nota**: Obtén tu API Key de Brevo en https://app.brevo.com/settings/keys/api

### 2. Instalar Dependencias

```powershell
cd backend
pip install -r requirements.txt
```

### 3. Inicializar Base de Datos

La base de datos se inicializa automáticamente al arrancar el servidor. El sistema incluye **migraciones automáticas** que detectan columnas faltantes:

- La función `_run_migrations()` en `database_sqlite.py` verifica si la columna `email` existe en la tabla `users`
- Si no existe, la añade automáticamente con su índice único
- Las tablas nuevas (como `password_reset_tokens`) se crean con `create_all()`

Si necesitas reiniciar manualmente:

**Opción A: Reiniciar la BD (⚠️ BORRA TODOS LOS DATOS)**
```powershell
Remove-Item cuentacuentos.db
```

**Opción B: Simplemente reinicia el servidor** (la migración automática se encarga)
```powershell
uvicorn main:app --reload
```

### 4. Iniciar el Servidor

```powershell
# Desde la raíz del proyecto
.\iniciar.ps1

# O directamente desde backend
cd backend
uvicorn main:app --reload
```

### 5. Probar con Swagger/OpenAPI

Abre http://localhost:8000/docs

**Test 1: Registrar usuario con email**
```json
POST /users/
{
  "username": "testuser",
  "email": "tu-email@ejemplo.com",
  "password": "password123"
}
```

**Test 2: Solicitar reset de contraseña**
```json
POST /forgot-password
{
  "email": "tu-email@ejemplo.com"
}
```

**Test 3: Revisar tu email**
- Busca el email de CuentaCuentos
- Copia el token del enlace (parámetro `?token=...`)

**Test 4: Resetear contraseña**
```json
POST /reset-password
{
  "token": "token_copiado_del_email",
  "new_password": "nuevaPassword456"
}
```

**Test 5: Login con nueva contraseña**
```
POST /token
username: testuser
password: nuevaPassword456
```

**Test 6: Cambiar contraseña (autenticado)**
```json
POST /change-password
Authorization: Bearer {tu_access_token}
{
  "current_password": "nuevaPassword456",
  "new_password": "otraPassword789"
}
```

### 6. Probar con cURL

```bash
# 1. Solicitar reset
curl -X POST http://localhost:8000/forgot-password \
  -H "Content-Type: application/json" \
  -d '{"email": "tu-email@ejemplo.com"}'

# 2. Resetear (reemplaza TOKEN)
curl -X POST http://localhost:8000/reset-password \
  -H "Content-Type: application/json" \
  -d '{"token": "TOKEN_DEL_EMAIL", "new_password": "nueva123"}'

# 3. Login para obtener token
curl -X POST http://localhost:8000/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=nueva123"

# 4. Cambiar contraseña (reemplaza ACCESS_TOKEN)
curl -X POST http://localhost:8000/change-password \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ACCESS_TOKEN" \
  -d '{"current_password": "nueva123", "new_password": "final456"}'
```

---

## ⏳ Pendiente (Frontend)

Las siguientes páginas/componentes deben ser implementadas en el frontend:

### Página: "Olvidé mi contraseña"
**Ubicación sugerida:** `/forgot-password`

**Funcionalidad:**
- Formulario con campo de email
- Validación de formato de email
- Llamada a `POST /forgot-password`
- Mensaje de éxito (siempre, por seguridad)

**Diseño sugerido:**
```html
<form>
  <input type="email" placeholder="Tu email" required />
  <button>Enviar enlace de recuperación</button>
</form>
<p>Recibirás un email si la cuenta existe</p>
```

### Página: "Restablecer contraseña"
**Ubicación sugerida:** `/reset-password?token=...`

**Funcionalidad:**
- Extraer token de query params
- Formulario con:
  - Campo de nueva contraseña
  - Campo de confirmar contraseña
  - Validación de coincidencia
- Llamada a `POST /reset-password`
- Redirección a login en éxito

**Diseño sugerido:**
```html
<form>
  <input type="password" placeholder="Nueva contraseña" required />
  <input type="password" placeholder="Confirmar contraseña" required />
  <button>Restablecer contraseña</button>
</form>
```

### Página: "Mi Perfil"
**Ubicación sugerida:** `/profile` (autenticada)

**Funcionalidad:**
- Mostrar información del usuario
- Sección de cambio de contraseña:
  - Campo de contraseña actual
  - Campo de nueva contraseña
  - Campo de confirmar nueva contraseña
- Llamada a `POST /change-password`
- Mensaje de confirmación

**Diseño sugerido:**
```html
<section>
  <h2>Cambiar Contraseña</h2>
  <form>
    <input type="password" placeholder="Contraseña actual" required />
    <input type="password" placeholder="Nueva contraseña" required />
    <input type="password" placeholder="Confirmar nueva" required />
    <button>Cambiar contraseña</button>
  </form>
</section>
```

---

## 📋 Checklist de Producción

Antes de desplegar a producción, verifica:

- [ ] Variable `SECRET_KEY` configurada (>= 32 caracteres aleatorios)
- [ ] API Key de Brevo configurada y verificada
- [ ] Email sender verificado en Brevo
- [ ] Variable `FRONTEND_URL` apunta al dominio de producción
- [ ] `FRONTEND_URL` usa HTTPS
- [ ] CORS configurado con dominios específicos (no `*`)
- [ ] Rate limiting configurado en nginx/API
- [ ] Logs de seguridad habilitados
- [ ] Backup de base de datos configurado
- [ ] Tarea programada para limpiar tokens expirados

---

## 🆘 Troubleshooting

### Error: "BREVO_API_KEY no configurada"
**Solución:** Agrega `BREVO_API_KEY=xkeysib-...` a tu `.env`

### Los emails no se envían
**Verificar:**
1. API Key válida en Brevo
2. Email sender verificado en Brevo
3. Cuota de Brevo no agotada (plan gratuito: 300/día)
4. Revisar logs del servidor para errores

### Error: "Token inválido o expirado"
**Posibles causas:**
- Token expiró (>1 hora)
- Token ya fue usado
- Token no existe en la BD
- Formato de token incorrecto

### Los tokens no expiran
**Solución:** Ejecuta manualmente:
```python
from models.database_sqlite import SessionLocal, delete_expired_tokens
db = SessionLocal()
delete_expired_tokens(db)
db.close()
```

### No se crea la tabla `password_reset_tokens`
**Solución:** Reinicia la BD o ejecuta:
```python
from models.database_sqlite import init_db
init_db()
```

---

## 📊 Estructura de Endpoints

```
POST   /users/                    # Registrar usuario
POST   /token                     # Login
GET    /users/me                  # Info del usuario autenticado

POST   /forgot-password            # Solicitar reset ✨ NUEVO
POST   /reset-password             # Resetear con token ✨ NUEVO
POST   /change-password            # Cambiar contraseña ✨ NUEVO
```

---

## 🎉 Próximas Mejoras Sugeridas

### Backend
- [ ] Rate limiting (máx 5 intentos/hora por IP)
- [ ] Validación de complejidad de contraseñas
- [ ] 2FA opcional con TOTP
- [ ] Logs de auditoría de cambios de contraseña
- [ ] Notificación de login desde nuevos dispositivos
- [ ] Configurar Alembic para migraciones
- [ ] Tarea programada (Celery) para limpiar tokens

### Frontend
- [ ] Indicador de fortaleza de contraseña
- [ ] Generador de contraseñas seguras
- [ ] Animaciones en transiciones de formularios
- [ ] Modo oscuro
- [ ] Internacionalización (i18n)

---

## 📚 Referencias

- [Documentación completa](docs/guides/password-reset.md)
- [Brevo API Docs](https://developers.brevo.com/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)

---

**¡Sistema de reset de contraseña completamente funcional!** 🎉

Ahora solo falta implementar las páginas del frontend para completar la experiencia de usuario.
