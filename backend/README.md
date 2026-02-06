# Backend - CuentaCuentos AI

Este directorio contiene la implementación del **backend API REST** del sistema CuentaCuentos AI, una aplicación FastAPI modular que funciona como un servicio independiente para la generación evolutiva de cuentos infantiles.

## 🏗️ Arquitectura y Estado

La aplicación sigue una **arquitectura API-first**, con el backend completamente separado del frontend. Esto permite que múltiples clientes (web, móvil, etc.) puedan consumir la misma API.

### ✅ Estado del Backend: **Completado y Funcional**

- [x] **API REST modular** con FastAPI.
- [x] **Integración completa con Google Gemini** para generación, crítica y síntesis.
- [x] **Bucle de Aprendizaje Evolutivo** implementado y activo.
- [x] **Sistema RAG (Retrieval-Augmented Generation)** implementado y activo.
- [x] **Base de datos dual:** Configurado para usar **SQLite** por defecto (desarrollo) y **PostgreSQL** como opción para producción.
- [x] **Documentación de API automática** vía Swagger y ReDoc.

## 🚀 Configuración y Ejecución

### 1. Requisitos Previos
- Python 3.9+

### 2. Instalar Dependencias
```powershell
# Navegar a la carpeta backend
cd backend

# Crear y/o activar el entorno virtual
# (El repositorio ya incluye una configuración de .venv)
.\.venv\Scripts\Activate.ps1

# Instalar dependencias
pip install -r requirements.txt
```

### 3. Configurar Variables de Entorno
Este paso es **crítico** para que la aplicación funcione.

```powershell
# Desde la carpeta 'backend', copia el archivo de ejemplo
Copy-Item .env.example .env
```

Luego, edita el nuevo archivo `.env` y añade tu clave de API de Google Gemini:

```env
# API Key de Google Gemini (REQUERIDO)
GEMINI_API_KEY=tu_api_key_aqui

# Base de Datos (SQLite por defecto para desarrollo)
# No necesitas cambiar esto para empezar.
DATABASE_URL=sqlite:///./cuentacuentos.db
```
> 🔑 **Obtén tu API key en:** https://aistudio.google.com/app/apikey

### 4. Ejecutar el Servidor
La base de datos SQLite se creará y se inicializará automáticamente la primera vez que inicies el servidor.

```powershell
# Desde la carpeta 'backend' (con el entorno virtual activado)
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

### 5. Verificar la Instalación
Una vez que el servidor esté en marcha, puedes acceder a las siguientes URLs:
- **API Docs (Swagger):** `http://localhost:8000/docs`
- **Health Check:** `http://localhost:8000/health`

El Health Check debería devolver un JSON confirmando que todos los componentes (Gemini, Base de datos, etc.) están configurados correctamente.

## 🗃️ Base de Datos

- **Desarrollo (Por defecto):** Se utiliza **SQLite**, que no requiere instalación adicional. El archivo `cuentacuentos.db` se creará en el directorio `backend/`.
- **Producción (Opcional):** La aplicación está preparada para usar **PostgreSQL** con la extensión `pgvector` para un rendimiento superior en búsquedas semánticas. Para usarla, instala las dependencias comentadas en `requirements.txt` y modifica la variable `DATABASE_URL` en tu archivo `.env`.

## 📋 API Endpoints Principales

La API está completamente documentada en la interfaz de Swagger (`/docs`). Los endpoints más importantes son:

- `POST /stories/generate`: El endpoint principal. Genera un cuento completo, lo guarda, y dispara el ciclo de crítica y aprendizaje.
- `GET /stories`: Lista todos los cuentos guardados.
- `GET /characters`: Lista los personajes disponibles.
- `GET /learning/statistics`: Muestra estadísticas sobre el proceso de aprendizaje de la IA.
- `GET /learning/lessons`: Lista las lecciones que la IA ha aprendido.
- `GET /rag/search`: Endpoint de prueba para la funcionalidad de búsqueda semántica (RAG).

---
**Para más detalles sobre la arquitectura, consulta el documento [`/docs/ARCHITECTURE.md`](../docs/ARCHITECTURE.md).**