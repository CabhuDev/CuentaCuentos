# CuentaCuentos AI - Documentación del Proyecto

## 📖 Visión General

CuentaCuentos AI es un generador inteligente de cuentos personalizados para niños que utiliza inteligencia artificial (Google Gemini) con una arquitectura API-first que permite escalabilidad y flexibilidad.

## 🏗️ Arquitectura API-First

### Separación Backend/Frontend

**Backend (API REST)**
- Puerto: `http://localhost:8000`
- Framework: FastAPI
- Responsabilidad: Lógica de negocio, IA, persistencia de datos
- Endpoints documentados en `/docs`

**Frontend (Cliente Web)**
- Puerto: `http://localhost:3000` (servidor independiente)
- Tecnología: HTML/CSS/JavaScript puro
- Responsabilidad: Interfaz de usuario, consumo de API
- Comunicación: REST API con fetch()

### Ventajas de esta arquitectura:
1. **Escalabilidad**: Backend puede servir múltiples frontends (web, móvil, etc.)
2. **Mantenibilidad**: Separación clara de responsabilidades
3. **Flexibilidad**: Tecnologías independientes, actualizaciones separadas
4. **Testing**: Pruebas independientes de API y UI
5. **Despliegue**: Estrategias de despliegue diferenciadas

## 🔄 Flujo de Datos

```
Frontend (UI) <--HTTP/REST--> Backend (API) <--> Database
                                    ↓
                            Google Gemini AI
```

### Proceso de Generación:
1. **Usuario completa formulario** en frontend
2. **Frontend envía POST** a `/stories/generate`
3. **Backend procesa** con servicios modulares
4. **IA genera contenido** usando Gemini API
5. **Backend retorna JSON** con cuento y crítica
6. **Frontend renderiza** resultado al usuario

## 📁 Estructura Detallada

### Backend Modular (/backend/)
```
backend/
├── main.py                    # App FastAPI con CORS habilitado
├── config.py                  # Variables de entorno centralizadas
├── models/
│   ├── database.py           # SQLAlchemy ORM + pgvector
│   └── schemas.py            # Pydantic validation models
├── services/                 # Capa de lógica de negocio
│   ├── character_service.py  # Gestión de personajes
│   ├── prompt_service.py     # Construcción de prompts
│   └── gemini_service.py     # Integración con IA
├── routers/                  # Endpoints REST organizados
│   ├── characters.py         # CRUD personajes
│   ├── stories.py            # Generación de cuentos
│   └── critiques.py          # Análisis y críticas
└── data/                     # Configuración JSON
    ├── characters.json       # Biblioteca de personajes
    ├── style_guide.json      # Guías de estilo
    └── learning_history.json # Historial de aprendizaje
```

### Frontend Independiente (/frontend/)
```
frontend/
├── index.html               # SPA principal
├── css/
│   └── styles.css           # Responsive design
└── js/
    └── app.js               # API client + DOM manipulation
```

## 🛠️ Stack Tecnológico Completo

### Backend Stack
| Tecnología | Propósito | Estado |
|------------|-----------|---------|
| FastAPI | Web framework REST | ✅ Implementado |
| SQLAlchemy | ORM + Database abstraction | ✅ Implementado |
| PostgreSQL | Base de datos principal | ✅ Configurado |
| pgvector | Embeddings vectoriales | ✅ Configurado |
| Pydantic | Data validation | ✅ Implementado |
| Google Gemini | IA generativa | ✅ Integrado |
| python-dotenv | Environment management | ✅ Implementado |

### Frontend Stack
| Tecnología | Propósito | Estado |
|------------|-----------|---------|
| HTML5 | Estructura de contenido | ✅ Implementado |
| CSS3 | Estilos responsive | ✅ Implementado |
| JavaScript ES6+ | Lógica de cliente | ✅ Implementado |
| Fetch API | HTTP requests | ✅ Implementado |

## 🔌 API Endpoints Documentados

### Personajes (/characters)
```http
GET /characters
Response: Array<Character>

POST /characters
Body: Character
Response: Character
```

### Cuentos (/stories)
```http
POST /stories/generate
Body: StoryPromptInput
Response: StoryResponse

GET /stories/{id}
Response: Story
```

### Críticas (/critiques)
```http
GET /critiques/{story_id}
Response: Critique
```

### Sistema (/health)
```http
GET /
Response: {"status": "healthy", "api_docs": "/docs"}

GET /health
Response: Detailed system status
```

## 🔧 Configuración de Desarrollo

### Variables de Entorno (.env)
```bash
# Base de datos PostgreSQL
DATABASE_URL=postgresql://usuario:password@localhost/cuentacuentos

# Google Gemini AI
GEMINI_API_KEY=tu_api_key_aquí

# Configuración de aplicación
APP_TITLE=CuentaCuentos AI API
APP_DESCRIPTION=API para generar cuentos personalizados para niños con IA
APP_VERSION=1.0.0

# Rutas de archivos de configuración
CHARACTERS_FILE=./data/characters.json
STYLE_GUIDE_FILE=./data/style_guide.json
STYLE_PROFILE_FILE=./data/style_profile.json
LEARNING_HISTORY_FILE=./data/learning_history.json
```

### Setup Backend
```bash
# 1. Navegar al backend (entorno virtual ya configurado)
cd backend

# 2. Activar entorno virtual
.venv\Scripts\Activate.ps1  # Windows PowerShell
.venv\Scripts\activate.bat  # Windows CMD
source .venv/bin/activate   # Linux/macOS

# 3. Verificar dependencias instaladas
pip list

# 4. Instalar dependencias si es necesario
pip install fastapi uvicorn sqlalchemy psycopg2-binary python-dotenv google-generativeai pgvector

# 5. Configurar .env (ver arriba)

# 6. Ejecutar servidor
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

### Setup Frontend
```bash
# Servidor HTTP simple para desarrollo
cd frontend
python -m http.server 3000

# O usar Live Server en VS Code
# Instalar extensión "Live Server" y clic derecho en index.html > "Open with Live Server"
```

## 🔗 Integración Frontend-Backend

### JavaScript API Client
```javascript
const API_BASE_URL = 'http://127.0.0.1:8000';

// Cargar personajes disponibles
async function loadCharacters() {
    const response = await fetch(`${API_BASE_URL}/characters`);
    return await response.json();
}

// Generar cuento
async function generateStory(storyData) {
    const response = await fetch(`${API_BASE_URL}/stories/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(storyData)
    });
    return await response.json();
}
```

### CORS Configuration
```python
# En main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción: ["https://tu-frontend.com"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 📊 Flujos de Datos

### 1. Carga de Personajes
```
Frontend                Backend              Data
   |                       |                  |
   |-- GET /characters --> |                  |
   |                       |-- load_file --> |
   |                       |<-- JSON -------- |
   |<-- Array<Character> --|                  |
   |                       |                  |
```

### 2. Generación de Cuento
```
Frontend                Backend              AI Service           Database
   |                       |                     |                   |
   |-- POST /stories/ ---> |                     |                   |
   |    generate            |-- build_prompt --> |                   |
   |                       |-- call_gemini ----> |                   |
   |                       |<-- story_text ----- |                   |
   |                       |-- store_story ------|-----------------> |
   |<-- StoryResponse ---- |                     |                   |
```

## 🧪 Testing

### Backend Testing
```bash
# Instalar dependencias de testing
pip install pytest pytest-asyncio httpx

# Estructura de tests
backend/tests/
├── test_characters.py    # Test endpoints de personajes
├── test_stories.py       # Test generación de cuentos
├── test_services.py      # Test lógica de negocio
└── conftest.py           # Configuración pytest

# Ejecutar tests
pytest tests/ -v
```

### Frontend Testing
```bash
# Testing manual con diferentes navegadores
# Testing de API usando Postman/Insomnia
# Testing E2E con Playwright (opcional)
```

## 🚀 Estrategias de Despliegue

### Backend (API)
```dockerfile
# Dockerfile para backend
FROM python:3.13-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Opciones de despliegue:**
- **Heroku**: Simple con `Procfile`
- **Railway**: Deploy directo desde Git
- **DigitalOcean App Platform**: Escalable
- **AWS ECS/Lambda**: Para alta disponibilidad

### Frontend (SPA)
**Opciones de hosting estático:**
- **Vercel**: Deploy automático desde Git
- **Netlify**: CDN global incluido
- **GitHub Pages**: Gratuito para repositorios públicos
- **AWS S3 + CloudFront**: Máximo control

### Configuración de Producción
```javascript
// En frontend/js/app.js para producción
const API_BASE_URL = process.env.NODE_ENV === 'production' 
    ? 'https://tu-api.herokuapp.com'
    : 'http://127.0.0.1:8000';
```

## 🔄 Workflow de Desarrollo

### Git Workflow
```bash
# Desarrollo de feature
git checkout -b feature/nueva-funcionalidad
# ... hacer cambios en backend O frontend
git commit -am "Add: nueva funcionalidad en [backend|frontend]"
git push origin feature/nueva-funcionalidad

# Merge a main
git checkout main
git merge feature/nueva-funcionalidad
```

### Versionado Independiente
- Backend: API versioning en URLs (`/v1/stories/generate`)
- Frontend: Versionado en package.json o tags Git
- Base de datos: Migraciones con Alembic

## 📈 Monitoring y Observabilidad

### Backend Metrics
```python
# En main.py - agregar middleware de métricas
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(f"{request.method} {request.url} - {response.status_code} - {process_time:.2f}s")
    return response
```

### Health Checks
- Backend: `/health` endpoint con métricas detalladas
- Frontend: Verificación de conectividad con API
- Base de datos: Connection pooling y timeouts

## 🔧 Troubleshooting

### Problemas Comunes

**CORS Errors**
```bash
# Verificar configuración CORS en main.py
# Verificar que allow_origins incluya el dominio del frontend
```

**API Key Issues**
```bash
# Verificar .env está configurado
# Verificar GEMINI_API_KEY es válido
# Verificar límites de rate en Google Cloud Console
```

**Database Connection**
```bash
# Verificar PostgreSQL está ejecutándose
# Verificar DATABASE_URL es correcto
# Verificar extensión pgvector está instalada
```

## 🎯 Roadmap Futuro

### Próximas Funcionalidades
- [ ] **Autenticación de usuarios** (JWT tokens)
- [ ] **Multilenguaje** (i18n)
- [ ] **Historiales de cuentos por usuario**
- [ ] **Exportación a PDF/ePub**
- [ ] **API de imágenes** (DALL-E integration)
- [ ] **Caching Redis** para mejorar performance
- [ ] **WebSockets** para generación en tiempo real
- [ ] **Mobile app** (React Native/Flutter)

### Optimizaciones Técnicas
- [ ] **Database migrations** con Alembic
- [ ] **API rate limiting** con slowapi
- [ ] **Response caching** para endpoints frecuentes
- [ ] **Async database** con asyncpg
- [ ] **Background tasks** con Celery
- [ ] **Logging estructurado** con structlog

---

*Documentación actualizada para arquitectura API-first - v1.0.0*