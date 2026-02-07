# Backend - CuentaCuentos AI

Este directorio contiene el **backend API REST** del proyecto, desarrollado con **FastAPI**.

## 🏗️ Arquitectura y Estado

La aplicación sigue una arquitectura modular y está en estado **completamente funcional**.

- ✅ **API REST modular** con FastAPI (`routers` y `services`).
- ✅ **Integración completa con Google Gemini** para generación, crítica y síntesis.
- ✅ **Bucle de Aprendizaje Evolutivo** implementado y activo.
- ✅ **Sistema RAG (Retrieval-Augmented Generation)** implementado y activo.
- ✅ **Base de datos dual:** SQLite para desarrollo y preparada para PostgreSQL en producción.
- ✅ **Documentación de API automática** en `/docs` (Swagger) y `/redoc`.

Para una visión completa de la arquitectura del sistema, consulta el documento principal: **[🏗️ `docs/architecture.md`](../docs/architecture.md)**.

## 🚀 Instalación y Ejecución

Las instrucciones detalladas para la configuración del entorno y la ejecución del proyecto se encuentran en la raíz:

- **Guía de Inicio Rápido:** **[🚀 `README.md`](../README.md)**
- **Guía para Contribuidores:** **[🤝 `CONTRIBUTING.md`](../CONTRIBUTING.md)**

Una vez en marcha, puedes verificar la salud del backend en `http://localhost:8000/health`.

## 🗃️ Base de Datos

- **Desarrollo (Por defecto):** Se utiliza **SQLite**. El archivo `cuentacuentos.db` se creará en este mismo directorio.
- **Producción (Opcional):** La aplicación está preparada para usar **PostgreSQL** con la extensión `pgvector`. Para ello, modifica la variable `DATABASE_URL` en tu archivo `.env`.

## 📋 API Endpoints Principales

La API está completamente documentada en la interfaz de Swagger (`/docs`). Los endpoints más importantes son:

- `POST /stories/generate`: Genera un cuento, lo guarda, y dispara el ciclo de crítica y aprendizaje.
- `GET /stories`: Lista todos los cuentos guardados.
- `GET /characters`: Lista los personajes disponibles.
- `GET /learning/statistics`: Muestra estadísticas sobre el proceso de aprendizaje de la IA.
- `GET /learning/lessons`: Lista las lecciones que la IA ha aprendido.
- `GET /rag/search`: Endpoint de prueba para la funcionalidad de búsqueda semántica (RAG).