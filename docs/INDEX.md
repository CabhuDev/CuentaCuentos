# 📚 Índice de Documentación - CuentaCuentos AI

## 📖 Documentos Principales

### Getting Started
- **[README.md](../README.md)** - Punto de entrada principal al proyecto
- **[CONTRIBUTING.md](../CONTRIBUTING.md)** - Guía para contribuidores
- **[CHANGELOG.md](../CHANGELOG.md)** - Historial de cambios y versiones

### Planificación
- **[ROADMAP.md](../ROADMAP.md)** - Estado actual y planes futuros
- **[LICENSE](../LICENSE)** - Licencia MIT del proyecto

## 🏗️ Arquitectura y Diseño

### Core
- **[docs/ARCHITECTURE.md](ARCHITECTURE.md)** - Arquitectura completa del sistema
  - Arquitectura API-First
  - Bucle de aprendizaje evolutivo
  - Sistema de autenticación y seguridad
  - Componentes y flujos de datos

- **[docs/literary-quality.md](literary-quality.md)** - Técnicas de calidad literaria
  - 6 técnicas profesionales implementadas
  - Ejemplos de aplicación
  - Guía de estilo narrativo

## 🔒 Seguridad

- **[docs/security.md](security.md)** - Guía completa de seguridad
  - Gestión de API keys (Gemini, ElevenLabs, Brevo)
  - Protección de SECRET_KEY
  - Tokens de reset de contraseña
  - Auditoría y mejores prácticas
  - Checklist antes de commits

## 🚀 Despliegue y Operaciones

- **[docs/deployment-vps.md](deployment-vps.md)** - Despliegue en producción
  - Configuración de VPS
  - Docker y Nginx
  - PostgreSQL vs SQLite
  - Variables de entorno de producción

## 📘 Guías Específicas

### Integración de Servicios

- **[docs/guides/elevenlabs-tts.md](guides/elevenlabs-tts.md)** - Text-to-Speech
  - Integración con ElevenLabs
  - Configuración de voces
  - Generación de audio
  - API y endpoints

- **[docs/guides/password-reset.md](guides/password-reset.md)** - Sistema de contraseñas ⭐ NUEVO
  - Configuración de Brevo
  - Flujo de reset de contraseña
  - Endpoints de autenticación
  - Seguridad y mejores prácticas
  - Guía de testing

## 📝 Resúmenes de Implementación

- **[IMPLEMENTACION-PASSWORD-RESET.md](../IMPLEMENTACION-PASSWORD-RESET.md)** - Resumen ejecutivo
  - Cambios realizados en backend
  - Pruebas y configuración
  - Tareas pendientes de frontend
  - Troubleshooting

## 🗂️ Estructura de Carpetas

```
docs/
├── ARCHITECTURE.md           # Arquitectura completa
├── literary-quality.md       # Calidad literaria
├── security.md               # Guía de seguridad
├── deployment-vps.md         # Despliegue en producción
└── guides/                   # Guías específicas
    ├── elevenlabs-tts.md     # Integración TTS
    └── password-reset.md     # Sistema de contraseñas ⭐
```

## 🔍 Búsqueda Rápida por Tema

### Quiero aprender sobre...

#### **Arquitectura y Diseño**
→ [ARCHITECTURE.md](ARCHITECTURE.md)

#### **Cómo funciona el aprendizaje evolutivo**
→ [ARCHITECTURE.md](ARCHITECTURE.md) (sección "Bucle de Aprendizaje")

#### **Calidad de los cuentos generados**
→ [literary-quality.md](literary-quality.md)

#### **Autenticación y JWT**
→ [ARCHITECTURE.md](ARCHITECTURE.md) (sección "Sistema de Autenticación")
→ [security.md](security.md)

#### **Reset de contraseña**
→ [guides/password-reset.md](guides/password-reset.md) ⭐
→ [IMPLEMENTACION-PASSWORD-RESET.md](../IMPLEMENTACION-PASSWORD-RESET.md)

#### **Text-to-Speech con ElevenLabs**
→ [guides/elevenlabs-tts.md](guides/elevenlabs-tts.md)

#### **Seguridad de API Keys**
→ [security.md](security.md)

#### **Despliegue a producción**
→ [deployment-vps.md](deployment-vps.md)

#### **Contribuir al proyecto**
→ [CONTRIBUTING.md](../CONTRIBUTING.md)

#### **Estado actual y roadmap**
→ [ROADMAP.md](../ROADMAP.md)

#### **Historial de cambios**
→ [CHANGELOG.md](../CHANGELOG.md)

## 📊 Matriz de Documentación por Rol

### Para Desarrolladores Backend
1. [ARCHITECTURE.md](ARCHITECTURE.md)
2. [security.md](security.md)
3. [CONTRIBUTING.md](../CONTRIBUTING.md)
4. [guides/password-reset.md](guides/password-reset.md)

### Para Desarrolladores Frontend
1. [README.md](../README.md)
2. [ARCHITECTURE.md](ARCHITECTURE.md) (sección API)
3. [guides/password-reset.md](guides/password-reset.md) (sección Frontend)
4. [IMPLEMENTACION-PASSWORD-RESET.md](../IMPLEMENTACION-PASSWORD-RESET.md)

### Para DevOps / Sysadmin
1. [deployment-vps.md](deployment-vps.md)
2. [security.md](security.md)
3. [ROADMAP.md](../ROADMAP.md)

### Para Arquitectos / Tech Leads
1. [ARCHITECTURE.md](ARCHITECTURE.md)
2. [ROADMAP.md](../ROADMAP.md)
3. [CHANGELOG.md](../CHANGELOG.md)

### Para Nuevos Contribuidores
1. [README.md](../README.md)
2. [CONTRIBUTING.md](../CONTRIBUTING.md)
3. [ROADMAP.md](../ROADMAP.md)
4. [security.md](security.md)

## 🆕 Últimas Actualizaciones (2026-02-09)

### Documentación Nueva
- ✨ [guides/password-reset.md](guides/password-reset.md) - Guía completa de reset de contraseña
- ✨ [IMPLEMENTACION-PASSWORD-RESET.md](../IMPLEMENTACION-PASSWORD-RESET.md) - Resumen de implementación
- ✨ [CHANGELOG.md](../CHANGELOG.md) - Historial de versiones
- ✨ Este índice de documentación

### Documentación Actualizada
- 📝 [ROADMAP.md](../ROADMAP.md) - Marcadas funcionalidades implementadas
- 📝 [ARCHITECTURE.md](ARCHITECTURE.md) - Sección de autenticación agregada
- 📝 [security.md](security.md) - Mejores prácticas para tokens
- 📝 [CONTRIBUTING.md](../CONTRIBUTING.md) - Nuevas variables de entorno
- 📝 [README.md](../README.md) - Referencias actualizadas
- 📝 [backend/.env.example](../backend/.env.example) - Variables completas

## 🔗 Enlaces Externos Útiles

### APIs y Servicios
- [Google Gemini API](https://aistudio.google.com/app/apikey) - Obtener API Key
- [ElevenLabs Dashboard](https://elevenlabs.io/) - Text-to-Speech
- [Brevo API](https://app.brevo.com/settings/keys/api) - Servicio de Email
- [FastAPI Docs](https://fastapi.tiangolo.com/) - Framework backend

### Recursos de Seguridad
- [OWASP Cheat Sheets](https://cheatsheetseries.owasp.org/)
- [JWT Best Practices](https://tools.ietf.org/html/rfc8725)
- [Python Passlib](https://passlib.readthedocs.io/)

### Estándares
- [Keep a Changelog](https://keepachangelog.com/es/1.0.0/)
- [Semantic Versioning](https://semver.org/lang/es/)
- [Conventional Commits](https://www.conventionalcommits.org/es/)

---

**Última actualización:** 9 de febrero de 2026

**Mantenedor:** [@CabhuDev](https://github.com/CabhuDev)

**¿Falta algo?** Abre un issue en GitHub o contribuye con un PR.
