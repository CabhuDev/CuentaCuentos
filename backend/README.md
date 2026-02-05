# Backend - CuentaCuentos AI

Este directorio contiene la implementación del **backend API REST** del sistema CuentaCuentos AI, una aplicación FastAPI modular que funciona como backend independiente en una arquitectura API-first para la generación evolutiva de cuentos infantiles con IA.

## 🏗️ Arquitectura API-First

La aplicación sigue una **arquitectura API-first** con backend completamente independiente del frontend:

```
backend/ (Puerto 8000)           ←→    frontend/ (Puerto 3000)
├── FastAPI + CORS                      ├── HTML/CSS/JavaScript  
├── API REST pura                       ├── Cliente HTTP (Fetch API)
├── Google Gemini 2.5 Flash ✅           └── Interfaz responsive
├── SQLite (desarrollo)
├── PostgreSQL + pgvector (opcional)
└── Sin dependencias frontend

Ventajas:
✅ Escalabilidad horizontal  
✅ Múltiples frontends (web, móvil, desktop)
✅ Desarrollo independiente
✅ Testing aislado
✅ Despliegue diferenciado
```

```
backend/
├── main.py                    # 🚀 Aplicación FastAPI principal
├── config.py                  # 🔧 Configuración centralizada
├── .env                       # 🔑 Variables de entorno (DATABASE_URL, GEMINI_API_KEY)
├── requirements.txt           # 📦 Dependencias Python
├── data/                      # 📁 Archivos de configuración JSON
├── models/                    # 🏗️ Capa de datos
├── services/                  # ⚙️ Lógica de negocio
├── routers/                   # 🛛️ Endpoints API
├── deprecated/                # 📦 Código obsoleto (respaldo)
└── .venv/                     # Python virtual environment
```

## 📁 Estructura Detallada

### `/data` - Archivos de Configuración
- **`characters.json`** - Definiciones de personajes con coherencia visual y narrativa
- **`style_guide.json`** - Guía de estilo flexible para generación de cuentos
- **`style_profile.json`** - Perfil evolutivo del sistema de escritura
- **`learning_history.json`** - Historial de lecciones sintetizadas
- **`critique_output.json`** - Ejemplo del formato de críticas automáticas

### `/models` - Capa de Datos
- **`database_sqlite.py`** - Modelos SQLAlchemy para SQLite (ACTIVO - desarrollo)
  - Usa JSON para embeddings en lugar de Vector
  - Compatible con SQLite sin dependencias adicionales
  - UUIDs como strings en lugar de tipo UUID nativo
  - **Campo `illustration_template`** - Plantilla JSON para generación de ilustraciones con IA
- **`schemas.py`** - Modelos Pydantic para validación de API

**Nota:** Para PostgreSQL con pgvector, usa los modelos en `deprecated/database_postgres_models.py`

### `/services` - Lógica de Negocio
- **`character_service.py`** - Gestión de personajes y coherencia narrativa
- **`prompt_service.py`** - Construcción inteligente de prompts para generación  
  - Integra lecciones aprendidas del sistema evolutivo
  - **✅ NUEVO** Integra ejemplos de RAG (cuentos similares exitosos)
  - Genera prompts híbridos: reglas + lecciones + ejemplos concretos
- **`gemini_service.py`** - **✅ ACTUALIZADO** Integración con Google Gemini usando el nuevo SDK `google-genai==0.2.2`
  - Migrado desde `google.generativeai` (deprecado)
  - Usa `Client()` en lugar de `configure()`
  - Modelo: `gemini-2.5-flash`
  - Métodos principales:
    * `generate_story()` - Genera contenido del cuento
    * `generate_critique()` - Crítica automática con análisis JSON
    * `generate_illustration_template()` - **NUEVO** Plantilla JSON para ilustraciones
    * `synthesize_lessons()` - **NUEVO** Sintetiza patrones de aprendizaje de críticas
    * `generate_embedding()` - Embeddings con `embed_content(contents=text)`
- **`learning_service.py`** - **✅ NUEVO** Sistema de aprendizaje evolutivo
  - Gestiona persistencia de `learning_history.json` y `style_profile.json`
  - Métodos principales:
    * `add_lessons_to_history()` - Añade lecciones sintetizadas
    * `update_style_profile()` - Actualiza métricas de evolución
    * `get_active_lessons()` - Filtra lecciones activas por categoría
    * `get_synthesis_statistics()` - Estadísticas del sistema de aprendizaje
    * `increment_lesson_application()` - Trackea uso de lecciones
- **`rag_service.py`** - **✅ NUEVO** Sistema RAG (Retrieval-Augmented Generation)
  - Búsqueda semántica de cuentos similares exitosos
  - Cache de embeddings para optimización
  - Similitud coseno con SQLite JSON embeddings
  - **✅ CORREGIDO** - Parsing de critique_text como JSON (línea 169)
  - Extracción de técnicas desde feedback.strengths[:3]
  - Parámetros: min_similarity=0.5, min_score=7.5, top_k=2
  - Métodos principales:
    * `search_similar_stories()` - Busca top-K cuentos similares con pre-filtrado
    * `get_theme_embedding()` - Embeddings con cache persistente
    * `cosine_similarity()` - Cálculo de similitud vectorial
  - Manejo robusto de errores con try/except en parsing JSON

### `/routers` - Endpoints API
- **`characters.py`** - CRUD de personajes (`GET /characters`)
- **`stories.py`** - **Generación automática** (`POST /stories/generate`) con:
  - **✅ RAG integrado** - Busca cuentos similares exitosos antes de generar
  - Embeddings semánticos para búsqueda
  - **Plantillas de ilustraciones automáticas** (JSON listo para IA de imágenes)
  - **Crítica automática en background** (BackgroundTasks)
  - **Síntesis automática cada 2 críticas** - Dispara análisis de patrones con Gemini
  - Trackeo de lecciones aplicadas
  - Gestión de cuentos (`GET /stories`, `GET /stories/{id}`)
- **`critiques.py`** - Críticas manuales y endpoint `GET /stories/{id}/critiques`
- **`learning.py`** - **✅ NUEVO** Sistema de aprendizaje evolutivo:
  - `POST /learning/synthesize` - Síntesis manual de lecciones
  - `GET /learning/statistics` - Estadísticas del sistema
  - `GET /learning/lessons` - Lista de lecciones con filtros
  - `GET /learning/history` - Historial completo JSON
  - `GET /learning/style-profile` - Perfil evolutivo JSON
- **`rag.py`** - **✅ FUNCIONAL** Testing y debugging de RAG:
  - `GET /rag/search?theme=hermanos&top_k=2` - Busca cuentos similares (✅ TESTEADO)
  - `GET /rag/stats` - Estadísticas: total stories, con embeddings, coverage % (✅ FRONTEND INTEGRADO)
  - `GET /rag/cache/status` - Estado del cache de embeddings
  - `DELETE /rag/cache/clear` - Limpiar cache
  - **Dashboard frontend**: aprendizaje.html con 4 cards de estadísticas RAG

### `/deprecated` - Código Obsoleto (Respaldo)
- **`README.md`** - Documentación de archivos deprecados
- **`main_old.py`** - Versión monolítica antigua (425 líneas)
- **`database_postgres.py`** - Configuración PostgreSQL duplicada
- **`database_postgres_models.py`** - Modelos con pgvector para PostgreSQL

## 🚀 Configuración y Ejecución

### Requisitos Previos
```bash
# Python 3.9+
# SQLite (incluido en Python)

# PostgreSQL OPCIONAL (solo si no usas SQLite):
CREATE DATABASE cuentacuentos_db;
CREATE EXTENSION vector;
```

### Instalación de Dependencias

El proyecto incluye un archivo `requirements.txt` actualizado:

```bash
# Framework web
fastapi==0.115.6
uvicorn==0.34.0

# Base de datos SQLite (incluido en Python)
sqlalchemy==2.0.36

# PostgreSQL - OPCIONAL (solo si usas PostgreSQL en lugar de SQLite)
# Descomenta estas líneas si necesitas PostgreSQL con pgvector:
# psycopg2-binary==2.9.10
# pgvector==0.3.6

# Validación de datos
pydantic==2.10.4
pydantic-settings==2.7.0

# Variables de entorno
python-dotenv==1.0.1

# API de Google Gemini (NUEVO SDK)
google-genai==0.2.2
google-genai==0.2.2
```

Para instalar todas las dependencias:
```bash
cd backend
.\.venv\Scripts\Activate.ps1  # Windows PowerShell
pip install -r requirements.txt
```

> **⚠️ Migración del SDK de Gemini**: El proyecto ha sido migrado del paquete deprecado `google-generativeai` al nuevo SDK oficial `google-genai`. Este cambio elimina los warnings de deprecación y utiliza los modelos más recientes (Gemini 2.5 Flash).

### Variables de Entorno (.env)
Crear archivo `.env` en la raíz del backend:
```bash
# Base de datos PostgreSQL con pgvector
DATABASE_URL=postgresql://usuario:password@localhost/cuentacuentos

# Google Gemini IA (✅ REQUERIDO para funcionalidad completa)
GEMINI_API_KEY=tu_google_gemini_api_key_aquí

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

### Entorno Virtual y Dependencias
```bash
# El proyecto tiene .venv preconfigurado en /backend/
# Para activar:
cd backend
.venv\Scripts\Activate.ps1  # Windows PowerShell

# Verificar instalación:
pip list

# Si necesitas reinstalar dependencias:
pip install fastapi uvicorn sqlalchemy psycopg2-binary python-dotenv google-generativeai pgvector
```

### Ejecutar Backend API
```bash
# Navegar al backend y activar entorno virtual
cd backend
.venv\Scripts\Activate.ps1  # Windows PowerShell
.venv\Scripts\activate.bat  # Windows CMD
source .venv/bin/activate    # Linux/macOS

# Instalar dependencias
pip install -r requirements.txt

# Configurar .env (ver sección anterior)

# Ejecutar servidor API en puerto 8000
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

**✅ API disponible en**: 
- **Swagger UI**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health  
- **Endpoint root**: http://localhost:8000/

### Verificación de Setup
```bash
# Verificar que la API responde
curl http://localhost:8000/health

# Debe retornar algo como:
{
  "status": "healthy",
  "characters_loaded": 1,
  "style_guide_loaded": true,
  "gemini_configured": true,
  "version": "1.0.0",
  "architecture": "API-first con frontend independiente"
}
```

### Inicializar Base de Datos
```python
# Descomenta una vez en main.py:
from models.database import create_tables
create_tables()
```

## 📋 API Endpoints (ACTUALIZADO)

### Sistema y Salud
- `GET /` - **Estado de la API** con información de arquitectura
- `GET /health` - **Verificación detallada** (personajes, Gemini, base de datos)
- `GET /docs` - **Documentación Swagger** interactiva
- `GET /redoc` - **Documentación ReDoc** alternativa

### Personajes  
- `GET /characters` - **Lista personajes** disponibles con detalles completos
- ~~`GET /characters/{id}`~~ - *(Implementación pendiente)*

### ✨ **Cuentos (FUNCIONALIDAD PRINCIPAL)**
- `POST /stories/generate` - **🎯 GENERACIÓN AUTOMÁTICA** con IA (endpoint principal)
  - Genera cuento completo
  - Crea embedding semántico
  - **Genera plantilla de ilustraciones** (JSON para IA de imágenes)
  - **Dispara crítica automática** en background
- `POST /stories/prompt` - Genera prompt estructurado (sin IA)
- `POST /stories` - Crea cuento manual (sin IA)
- `GET /stories` - Lista cuentos (Obtiene críticas de un cuento específico
- **Crítica automática**: Se genera en background al crear cuento (BackgroundTasks)

### 🧠 **Aprendizaje Evolutivo (NUEVO)**
- `POST /learning/synthesize` - **Síntesis manual** de lecciones (analiza últimas N críticas)
- `GET /learning/statistics` - **Estadísticas** del sistema de aprendizaje
  - Total de síntesis realizadas
  - Lecciones aprendidas y activas
  - Críticas hasta próxima síntesis
  - Score promedio de últimos 10 cuentos
- `GET /learning/lessons` - **Lista de lecciones** con filtros por categoría y estado
- `GET /learning/history` - **Historial completo** de learning_history.json
- `GET /learning/style-profile` - **Perfil de estilo** completo de style_profile.json
- **Síntesis automática**: Cada 2 críticas el sistema analiza patrones y aprende automáticamente

### Críticas y Análisis
- `POST /critiques` - Añade crítica manual a un cuento
- `GET /stories/{id}/critiques` - **NUEVO** Obtiene críticas de un cuento específico
- **Crítica automática**: Se genera en background al crear cuento (BackgroundTasks)

## 🌟 **Endpoint Principal: Generación Automática**

### `POST /stories/generate` 
**El endpoint más importante** - genera cuentos completos con IA:

```json
// Request
{
  "character_name": "Martín el Valiente",
  "theme": "Una aventura en el bosque mágico",
  "target_age": 6,
  "moral_lesson": "La importancia de la amistad",
  "length": "medium",
  "special_elements": "animales que hablan, magia"
}

// Response
{
  "story": {
    "id": "uuid-generado",
    "title": "Martín y los Secretos del Bosque Encantado",
    "content": "Era una mañana radiante cuando Martín...",
    "character_used": "Martín el Valiente",
    "target_age": 6,
    "created_at": "2024-02-04T10:30:00Z"
  },
  "critique": {
    "analysis": "El cuento presenta elementos apropiados para la edad...",
    "strengths": ["Vocabulario adecuado", "Mensaje claro"],
    "improvements": ["Incluir más descripción sensorial"]
  },
  "prompt_used": "Prompt completo enviado a Gemini..."
}
```

## 🧩 Componentes Clave (ACTUALIZADOS)

### 🤖 **Gemini Service (✅ IMPLEMENTADO)**
Integración completa con Google Gemini IA:
```python
from services.gemini_service import gemini_service

# Verificar configuración
if gemini_service.is_configured():
    # Generar cuento con Gemini 2.5 Flash
    story = await gemini_service.generate_story(prompt)
    
    # Generar crítica con Gemini 2.5 Flash
    critique = await gemini_service.generate_critique(story_content)
    
    # NUEVO: Generar plantilla de ilustraciones
    template = await gemini_service.generate_illustration_template(story_content, title)
    
    # Generar embedding semántico
    embedding = await gemini_service.generate_embedding(story_content)
```

### 🎭 **Character Service**  
Gestiona personajes con coherencia narrativa:
```python
from services.character_service import character_service

# Obtener personaje específico
character = character_service.get_character_by_name("Martín el Valiente")

# Listar todos los personajes
characters = character_service.get_all_characters()
```

### ⚙️ **Prompt Service**
Construye prompts inteligentes combinando múltiples fuentes:
```python
from services.prompt_service import prompt_service

# Construir prompt completo para IA
prompt_inputs = StoryPromptInput(
    character_name="Martín el Valiente",
    theme="aventura en el bosque",
    target_age=6
)
prompt = prompt_service.build_story_prompt(prompt_inputs)
```

## 🔄 Flujo de Trabajo Completo (CON IA)

### **Generación Automática** (`POST /stories/generate`)
1. **Input del Usuario** → `StoryGenerateInput` con personaje, tema, edad, etc.
2. **Resolución de Personaje** → Busca datos completos en `characters.json`  
3. **🧠 Síntesis Automática** → **✅ NUEVO** Cada 2 críticas, analiza patrones y aprende
10. **Construcción de Prompt** → Combina guía de estilo + personaje + contexto + historial
4. **🤖 Generación con IA** → **✅ Gemini 2.5 Flash** crea el cuento completo
5. **📊 Embedding Semántico** → Genera vector para búsqueda (text-embedding-004)
6. **🎨 Plantilla de Ilustraciones** → **✅ NUEVO** JSON con prompts para IA de imágenes
7. **💾 Almacenamiento** → Guarda en SQLite con embeddings + illustration_template
8. **🔍 Crítica Automática** → **✅ Background** Gemini analiza y guarda crítica
9. **📤 Respuesta** → Retorna cuento + plantilla + prompt usado (crítica en background)

### **Generación de Prompt** (`POST /stories/prompt`)  
1. **Input del Usuario** → `StoryPromptInput` básico
2. **Construcción Inteligente** → Combina múltiples fuentes de datos
3. **📤 Respuesta** → Retorna prompt estructurado (sin generar cuento)

### **Flujo de Datos**
```
Usuario → Frontend → Backend API → Gemini IA → PostgreSQL
                        ↓
                  Character Service
                  Prompt Service  
                  Style Guide
```

## 📊 Modelos de Datos

### Story (SQLite/PostgreSQL)
```sql
CREATE TABLE stories (
    id VARCHAR(36) PRIMARY KEY,  -- UUID como string en SQLite
    title VARCHAR(255),
    content TEXT NOT NULL,
    version INTEGER DEFAULT 1,
    is_seed BOOLEAN DEFAULT false,
    embedding_json JSON,  -- Vector en SQLite se guarda como JSON
    illustration_template JSON,  -- NUEVO: Plantilla para ilustraciones
    created_at TIMESTAMP
);
```

### Character (JSON)
```json
{
  "id": "martin_001",
  "nombre": "Martín",
  "rasgos_distintivos": {...},
  "personalidad_narrativa": {...},
  "reglas_ilustracion": {...}
}
```

## 🧪 Testing y Verificación

### **Testing Básico de la API**
```bash
# 1. Verificar salud del sistema
curl http://localhost:8000/health

# 2. Listar personajes disponibles  
curl http://localhost:8000/characters

# 3. 🎯 GENERAR CUENTO COMPLETO (Endpoint principal)
curl -X POST http://localhost:8000/stories/generate \
  -H "Content-Type: application/json" \
  -d '{
    "character_name": "Martín el Valiente", 
    "theme": "una aventura en el bosque",
    "target_age": 6,
    "length": "medium"
  }'

# 4. Solo generar prompt (sin IA)
curl -X POST http://localhost:8000/stories/prompt \
  -H "Content-Type: application/json" \
  -d '{
    "character_name": "Martín el Valiente",
    "theme": "una aventura en el bosque",
    "target_age": 6

# 5. 🧠 SINTETIZAR LECCIONES (Aprendizaje manual)
curl -X POST "http://localhost:8000/learning/synthesize?last_n_critiques=2" \
  -H "Content-Type: application/json"

# 6. Ver estadísticas de aprendizaje
curl http://localhost:8000/learning/statistics

# 7. Listar lecciones activas
curl "http://localhost:8000/learning/lessons?status_filter=active&category=pacing"

# 8. Ver historial completo de aprendizaje
curl http://localhost:8000/learning/history

# 9. Ver perfil de estilo actual
curl http://localhost:8000/learning/style-profile
  }'
```

### **Testing con Frontend**
Con el frontend ejecutándose en `http://localhost:3000`:
1. **Abrir interfaz web** en el navegador  
2. **Seleccionar personaje** del dropdown (carga desde API)
3. **Completar formulario** con tema, edad, etc.
4. **Generar cuento** - debería usar `POST /stories/generate`
5. **Verificar resultado** con cuento + análisis automático

### **Verificar Integración Gemini**
```python
# En Python console o script de test
from services.gemini_service import gemini_service

# Verificar configuración
print(f"Gemini configurado: {gemini_service.is_configured()}")

# Test de generación (requiere GEMINI_API_KEY)
if gemini_service.is_configured():
    story = await gemini_service.generate_story("Escribe un cuento corto sobre un gato")
    print(f"Historia generada: {story[:100]}...")
```

## 🔮 Estado de Desarrollo

### ✅ **COMPLETADO**
- ✅ **🧠 Bucle de aprendizaje evolutivo** con síntesis automática cada 2 críticas
- ✅ **Sistema de lecciones** con persistencia en JSON
- ✅ **Análisis de patrones** con Gemini para extraer insights
- ✅ **Auditoría de seguridad** completa para GitHub (ver `SECURITY.md`)

### 🔄 **EN DESARROLLO/PENDIENTE**
- [ ] **Aplicación de lecciones** a prompts de generación de cuentos
- [ ] **Tracking de efectividad** de lecciones aplicadas (A/B testing)
- [ ] **Búsqueda semántica** usando embeddings generados
- [ ] **Generación real de imágenes** usando illustration_template
- [ ] **Dashboard frontend** para visualizar evolución del aprendizaje
- [ ] **Cache de respuestas** para mejorar performance  
- [ ] **Rate limiting** y autenticación JWT
- [ ] **Testing automatizado** con pytest
- [ ] **Migraciones de DB** con Alembic
- [ ] **Logging estructurado** para produccióngreSQL + pgvector opcional)

### 🔄 **EN DESARROLLO/PENDIENTE**
- [ ] **Búsqueda semántica** usando embeddings generados
- [ ] **Síntesis de aprendizaje** periódica (cada N críticas)
- [ ] **Generación real de imágenes** usando illustration_template
- [ ] **Cache de respuestas** para mejorar performance  
- [ ] **Rate limiting** y autenticación JWT
- [ ] **Testing automatizado** con pytest
- [ ] **Migraciones de DB** con Alembic
- [ ] **Logging estructurado** para producción
- [ ] **Métricas** de calidad de cuentos generados

### ⚠️ **NOTAS IMPORTANTES**
- **Google Gemini Migration**: `google.generativeai` está deprecated → migrar a `google.genai`
- **CORS**: Configurado para `allow_origins=["*"]` en desarrollo → especificar dominios en producción
- **API Keys**: Nunca commitear en código fuente, usar `.env` y `.gitignore`
- **PostgreSQL**: Requiere extensión `vector` instalada
- **Frontend**: Ejecutar independientemente en puerto diferente (3000)

## 📝 Notas de Desarrollo

### **Arquitectura API-First**
- **Backend independiente:** No sirve archivos estáticos del frontend
- **CORS habilitado:** Permite acceso desde frontend en diferente puerto
- **Endpoints REST puros:** Comunicación solo vía JSON  
- **Documentación automática:** Swagger UI en `/docs`, ReDoc en `/redoc`

### **Servicios y Patterns**
- **Servicios singleton:** `character_service`, `prompt_service`, `gemini_service` mantienen estado
- **Dependency injection:** `Depends(db.get_db)` para sesiones de DB
- **Error handling:** Excepciones HTTP estructuradas en routers
- **Async/await:** Operaciones de IA son asíncronas para mejor performance

### **Configuración Modular**
- **Variables centralizadas:** Todo en `config.py` + `.env`
- **Imports absolutos:** Estructura lista para packaging  
- **Configuración por entorno:** Development vs production
- **Datos JSON:** Configuraciones rápidas sin DB para personajes y estilos

### **Integración con Frontend**
El frontend consume esta API desde `http://localhost:3000`:
## 🧠 Sistema de Aprendizaje Evolutivo

### **Visión General**
El sistema implementa un **bucle de aprendizaje automático** que analiza críticas de cuentos, identifica patrones y extrae lecciones para mejorar futuras generaciones.

### **Componentes del Sistema**
1. **Gemini Synthesis** - Análisis de patrones en lotes de críticas
2. **Learning Service** - Persistencia de lecciones y métricas
3. **Auto-Trigger** - Síntesis automática cada N críticas (configurable)
4. **JSON Storage** - `learning_history.json` y `style_profile.json`

### **Flujo de Aprendizaje**
```
Generar Cuento → Crítica Automática → Contador de Críticas
                                              ↓
                                      ¿Múltiplo de 5?
                                              ↓ Sí
                                    Gemini Synthesis
                                              ↓
                        Extrae: lessons_learned, style_adjustments
                                              ↓
                                    Learning Service
                                              ↓
                        Actualiza: learning_history.json
                                   style_profile.json
```

### **Configuración**
```python
# En backend/routers/stories.py
SYNTHESIS_THRESHOLD = 2  # Síntesis cada 2 críticas

# Para cambiar el umbral, modificar esta constante
# Valores recomendados: 2-10 críticas
```

### **Endpoints de Aprendizaje**
```bash
# Síntesis manual (últimas 5 críticas)
POST /learning/synthesize?last_n_critiques=5

# Estadísticas del sistema
GET /learning/statistics

# Lecciones filtradas
GET /learning/lessons?category=pacing&status_filter=active
```

### **Archivos de Datos**
- **`data/learning_history.json`** - Historial completo de síntesis
- **`data/style_profile.json`** - Perfil evolutivo del sistema

### **Documentación Completa**
Ver [`BUCLE-APRENDIZAJE.md`](../BUCLE-APRENDIZAJE.md) para guía detallada.

---

**🏗️ Para documentación completa del proyecto, ver [`README.md`](../README.md) en la raíz**  
**🔒 Para auditoría de seguridad, ver [`SECURITY.md`](../SECURITY.md)**  
**🧠 Para sistema de aprendizaje, ver [`BUCLE-APRENDIZAJE.md`](../BUCLE-APRENDIZAJE.md)
// Obtener personajes
const characters = await fetch(`${API_BASE_URL}/characters`).then(r => r.json());

// Generar cuento completo
const result = await fetch(`${API_BASE_URL}/stories/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(storyData)
});
```

---

**🏗️ Para documentación completa del proyecto, ver `/README.md` en la raíz**  
**📚 Para arquitectura detallada, ver `/docs/ARCHITECTURE.md`**