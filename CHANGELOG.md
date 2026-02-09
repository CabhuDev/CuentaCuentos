# Changelog

Todos los cambios notables en el proyecto CuentaCuentos AI se documentarán en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/lang/es/).

## [0.3.0] - 2026-02-09

### ✨ Agregado

#### Frontend React Dockerizado
- **Dockerfile Multi-Stage**: Build con Node 20 Alpine → Serve con Nginx Alpine
- **Nginx interno del contenedor**: SPA routing (try_files → index.html), compresión gzip, cache de assets Vite (1 año, immutable), no-cache para index.html
- **`.dockerignore`**: Optimización del contexto de build (excluye node_modules, dist, .git)
- **Contenedor `cuentacuentos_frontend`**: Puerto 8003 → 80 interno

#### Docker Compose Actualizado
- **Servicio `frontend`**: Multi-stage build desde `frontend-react/Dockerfile`
- **`depends_on`**: Frontend depende del backend
- **`restart: unless-stopped`**: Ambos contenedores se reinician automáticamente
- **Nombres de contenedores fijos**: `cuentacuentos_backend`, `cuentacuentos_frontend`
- **Eliminado `version: '3.8'`**: Obsoleto en Docker Compose moderno

#### Nginx VPS para Frontend Docker
- **Reverse proxy al contenedor**: `/cuentacuentos/` → `proxy_pass http://127.0.0.1:8003/`
- **Eliminado alias estático**: Ya no se sirven archivos desde `/var/www/cuentacuentos/frontend/`
- **Nuevos endpoints de auth**: `forgot-password`, `reset-password`, `change-password` redirigidos al backend

#### Scripts de Despliegue Actualizados
- **`deploy-cuentacuentos-frontend.ps1`**: Ahora usa `docker-compose up -d --build frontend` en vez de `scp` manual
- **`deploy-cuentacuentos-backend.ps1`**: Reconstruye solo servicio `backend` sin hacer down de todo
- **Verificación HTTP**: Ambos scripts verifican health check y respuesta del frontend

### 📝 Modificado

#### Documentación
- `docs/deployment-vps.md`: Reescrito completamente con guía de desarrollo local, arquitectura Docker, troubleshooting actualizado
- `docs/ARCHITECTURE.md`: Diagrama y estructura actualizados con contenedores Docker, tecnologías y nueva estructura de proyecto
- `CHANGELOG.md`: Entrada para v0.3.0

---

## [0.2.0] - 2026-02-09

### ✨ Agregado

#### Email de Bienvenida Automático
- **Email de Bienvenida**: Envío automático al registrar nuevo usuario
- **Templates de Brevo**: Integración con sistema de templates profesionales
  - Template de bienvenida (BREVO_WELCOME_TEMPLATE_ID)
  - Template de cambio de contraseña (BREVO_CHANGEPASS_TEMPLATE_ID)
- **Sincronización de Contactos**: Añade automáticamente usuarios a lista de Brevo
- **Función Genérica**: `_send_template_email()` para reutilizar lógica de envío
- **Gestión de Contactos**: `add_contact_to_list()` para sincronizar con Brevo

#### Sistema de Autenticación Completo
- **Registro y Login con JWT**: Sistema completo de autenticación basado en tokens JWT
- **Reset de Contraseña**: Funcionalidad completa para recuperar contraseña olvidada
  - Solicitud de reset por email
  - Generación de tokens seguros (256 bits, expiran en 1 hora)
  - Validación y uso único de tokens
  - Limpieza automática de tokens expirados
- **Cambio de Contraseña**: Endpoint para cambiar contraseña conociendo la actual
- **Campo de Email**: Agregado a usuarios para recuperación de cuenta

#### Servicio de Email con Brevo
- **Integración con Brevo API**: Sistema completo de envío de emails
- **Sistema de Templates**: Usa templates configurados en dashboard de Brevo
  - Función genérica `_send_template_email()` para reutilización
  - Parámetros dinámicos para personalización
- **Emails de Bienvenida**: Envío automático al registrar usuario
- **Emails de Reset**: Notificación con enlace seguro para restablecer contraseña
- **Emails de Confirmación**: Notificación cuando se cambia la contraseña usando template
- **Gestión de Contactos**: Sincronización automática con listas de Brevo
- **Plan Gratuito**: Soporte para 300 emails/día

#### Seguridad Mejorada
- **Hashing con Bcrypt**: Contraseñas hasheadas con salt único
- **Tokens Seguros**: Generación con `secrets.token_urlsafe(32)`
- **Expiración de Tokens**: Tokens de reset expiran en 1 hora
- **Tokens de Un Solo Uso**: Marcados como usados después de aplicarse
- **Mensajes Ambiguos**: No revela si un email existe en el sistema
- **Verificación de Contraseña**: Requiere contraseña actual para cambios

#### Base de Datos
- **Nueva Tabla**: `password_reset_tokens` para gestionar tokens de recuperación
- **Campo Email**: Agregado a tabla `users` (único, opcional)
- **Funciones CRUD**: Operaciones completas para usuarios y tokens

#### Documentación
- **Guía de Reset de Contraseña**: Documentación completa en `docs/guides/password-reset.md`
- **Resumen de Implementación**: `IMPLEMENTACION-PASSWORD-RESET.md` con instrucciones detalladas
- **Arquitectura Actualizada**: `docs/ARCHITECTURE.md` incluye sistema de autenticación
- **Seguridad Actualizada**: `docs/security.md` con mejores prácticas para tokens y API keys
- **ROADMAP Actualizado**: Funcionalidades implementadas y tareas pendientes
- **CHANGELOG**: Este archivo para seguimiento de versiones

### 📝 Modificado

#### Backend
- `models/database_sqlite.py`: Agregadas tablas y funciones para autenticación
- `models/schemas.py`: Nuevos schemas para operaciones de contraseña
- `services/auth_service.py`: Funciones extendidas para reset y cambio de contraseña
- `services/email_service.py`: Sistema de templates y gestión de contactos
  - `_send_template_email()`: Función genérica para templates de Brevo
  - `send_welcome_email()`: Email de bienvenida automático
  - `add_contact_to_list()`: Sincronización con listas de Brevo
  - `send_password_changed_confirmation()`: Ahora usa templates
- `routers/auth.py`: Tres nuevos endpoints de autenticación + envío automático de bienvenida
- `config.py`: Variables de configuración para Brevo (API Key, templates, lista)
- `requirements.txt`: Agregada dependencia `requests`

#### Documentación
- `README.md`: Actualizado con nuevas características
- `CONTRIBUTING.md`: Información sobre variables de entorno adicionales
- `ROADMAP.md`: Marcadas funcionalidades implementadas, actualizadas pendientes
- `docs/ARCHITECTURE.md`: Sección completa sobre autenticación
- `docs/security.md`: Mejores prácticas para API keys y tokens
- `backend/.env.example`: Variables de entorno completas y documentadas

### 🔒 Seguridad

- Implementado hashing de contraseñas con Bcrypt
- Tokens JWT firmados con SECRET_KEY configurable
- Tokens de reset generados criptográficamente seguros
- Expiración automática de tokens de reset
- Validación de contraseña actual antes de cambios
- Protección contra enumeración de usuarios
- Recomendaciones para HTTPS y rate limiting en producción

### 📋 Tareas Pendientes (Frontend)

- [x] Implementar página de login en React
- [x] Implementar página de registro en React
- [x] Implementar página "Olvidé mi contraseña"
- [x] Implementar página de reset de contraseña con token
- [x] Implementar página de perfil de usuario
- [x] Agregar sección de cambio de contraseña en perfil
- [x] Dockerizar frontend React con Nginx
- [ ] Implementar indicador de fortaleza de contraseña
- [ ] Agregar validación de confirmación de contraseña

---

## [0.1.0] - 2026-02-06

### ✨ Agregado

#### Sistema de Aprendizaje Evolutivo
- **Bucle Completo**: Generar → Criticar → Sintetizar → Aplicar
- **RAG (Retrieval-Augmented Generation)**: Búsqueda semántica de cuentos exitosos
- **Síntesis Automática**: Cada 2 críticas se sintetizan nuevas lecciones
- **Lecciones Persistentes**: Sistema de memoria con `learning_history.json`
- **Perfil de Estilo Evolutivo**: `style_profile.json` actualizado automáticamente

#### Generación de Audio (TTS)
- **Integración con ElevenLabs**: Text-to-Speech con voces naturales
- **Voz Profesional**: Narración con voz "George" (narrador cautivador)
- **Gestión de Audio**: Almacenamiento y streaming de archivos de audio
- **API de Audio**: Endpoints para generar y listar voces disponibles

#### Infraestructura
- **Arquitectura API-First**: Backend FastAPI y frontend desacoplados
- **Base de Datos Dual**: SQLite para desarrollo, PostgreSQL para producción
- **Embeddings para RAG**: Vectores semánticos con Gemini
- **Críticas Automáticas**: Sistema de evaluación en background
- **Personajes Persistentes**: Biblioteca de personajes reutilizables

#### Calidad Literaria
- **6 Técnicas Profesionales**: Basadas en literatura infantil clásica
- **Prompts Híbridos**: Combinación de reglas, lecciones y ejemplos
- **Evaluación Multi-dimensional**: Coherencia, estilo, ritmo, etc.

#### Documentación
- **Guía de Arquitectura**: Explicación completa del sistema
- **Guía de Calidad Literaria**: Técnicas de escritura implementadas
- **Guía de Seguridad**: Mejores prácticas para API keys
- **Guía de Despliegue**: Instrucciones para VPS y producción
- **Guía de TTS**: Integración con ElevenLabs

### 🚀 Inicializado

- Proyecto base con FastAPI y frontend vanilla
- Integración con Google Gemini
- Sistema de configuración con `.env`
- Scripts de utilidad para desarrollo
- Estructura modular y escalable

---

## Formato de Versiones

- **MAJOR.MINOR.PATCH**
- **MAJOR**: Cambios incompatibles en la API
- **MINOR**: Nuevas funcionalidades compatibles
- **PATCH**: Correcciones de errores

## Tipos de Cambios

- **Agregado**: Nuevas funcionalidades
- **Modificado**: Cambios en funcionalidades existentes
- **Depreciado**: Funcionalidades que se eliminarán pronto
- **Eliminado**: Funcionalidades eliminadas
- **Corregido**: Corrección de errores
- **Seguridad**: Mejoras de seguridad
