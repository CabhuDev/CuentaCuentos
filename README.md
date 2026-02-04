# CuentaCuentos AI: Sistema de Generación Evolutiva de Cuentos Infantiles

Este proyecto es un motor de escritura de cuentos infantiles basado en la API de Gemini, diseñado para aprender y mejorar su estilo narrativo de forma recursiva. Utiliza una arquitectura modular con persistencia de personajes y un bucle de retroalimentación para el aprendizaje evolutivo.

## ✨ Características Principales

- **Generación inteligente:** Cuentos para niños de 2-6 años con coherencia narrativa y visual
- **Personajes persistentes:** Mantiene consistencia de personajes a través de múltiples historias
- **Aprendizaje evolutivo:** Sistema de crítica automática y síntesis de lecciones
- **Guía de estilo flexible:** Framework adaptable para diferentes tipos de narrativas

## 🚀 Arquitectura Técnica

- **Framework:** FastAPI con arquitectura modular API-first
- **LLM:** Google Gemini 2.5 Flash (SDK: google-genai 0.2.2)
- **Base de Datos:** SQLite con embeddings JSON (desarrollo) / PostgreSQL con pgvector (producción opcional)
- **Frontend:** HTML/CSS/JavaScript vanilla (sin frameworks)
- **Patrón de Diseño:** RAG (Retrieval-Augmented Generation) + Arquitectura modular por capas

## 📁 Estructura del Proyecto

```
CuentaCuentos/
├── backend/                   # 🔧 API REST con FastAPI
│   ├── config.py              # Configuración centralizada
│   ├── main.py                # Aplicación FastAPI principal
│   ├── .env                   # Variables de entorno (DATABASE_URL, GEMINI_API_KEY)
│   ├── requirements.txt       # Dependencias Python
│   ├── data/                  # Archivos de configuración JSON
│   │   ├── characters.json    # Definiciones de personajes
│   │   ├── style_guide.json   # Guía de estilo narrativo
│   │   ├── style_profile.json # Perfil de estilo evolutivo (template)
│   │   ├── learning_history.json # Historial de lecciones (template)
│   │   └── critique_output.json  # Ejemplo de crítica (template)
│   ├── models/                # Capa de datos
│   │   ├── database_sqlite.py # Modelos SQLAlchemy para SQLite (ACTIVO)
│   │   └── schemas.py         # Modelos Pydantic (validación API)
│   ├── services/              # Lógica de negocio
│   │   ├── character_service.py  # Gestión de personajes
│   │   ├── prompt_service.py     # Construcción de prompts
│   │   └── gemini_service.py     # SDK google-genai (embeddings + generación)
│   ├── routers/               # Endpoints API
│   │   ├── characters.py      # GET /characters
│   │   ├── stories.py         # POST /stories/generate, GET /stories
│   │   └── critiques.py       # POST /critiques
│   ├── deprecated/            # Código obsoleto (respaldo)
│   │   ├── README.md          # Documentación de archivos deprecados
│   │   ├── main_old.py        # Versión monolítica antigua
│   │   ├── database_postgres.py        # Configuración PostgreSQL
│   │   └── database_postgres_models.py # Modelos con pgvector
│   ├── .venv/                 # Entorno virtual Python
│   └── README.md              # 📖 Documentación del backend
├── frontend/                  # 🎨 Interfaz Web (sin frameworks)
│   ├── index.html             # Página de generación de cuentos
│   ├── cuentos.html           # Página de biblioteca de cuentos
│   ├── css/
│   │   └── styles.css         # Estilos compartidos
│   ├── js/
│   │   ├── app.js             # Lógica del generador (con logs)
│   │   └── cuentos.js         # Lógica de la biblioteca
│   └── README.md              # 📖 Documentación del frontend
├── iniciar.ps1                # Script PowerShell para iniciar todo
├── PROJECT_STATUS.md          # Estado actual y roadmap
├── SOLUCION-ERRORES.md        # Soluciones implementadas
├── RESUMEN-LIMPIEZA.md        # Informe de limpieza de código
└── README.md                  # Este archivo
```

## 🛠️ Componentes del Sistema

1. **The Writer (Generador):** Produce cuentos basados en la guía de estilo actual y lecciones previas
2. **The Editor (Evaluador):** Analiza cuentos generados y extrae métricas de calidad
3. **The Archivist (Memoria):** Gestiona la base de datos vectorial y el historial evolutivo
4. **Character Manager:** Mantiene coherencia de personajes a través de historias

## 🔄 Flujo de Trabajo

1. **Input del Usuario:** Personaje + contexto opcional + parámetros narrativos
2. **Resolución de Personaje:** Busca en `characters.json` para mantener coherencia
3. **Construcción de Prompt:** Combina guía de estilo + datos del personaje + lecciones aprendidas
4. **Generación:** Gemini 2.5 Pro genera el cuento siguiendo el prompt estructurado
5. **Crítica Automática:** Gemini 2.5 Pro evalúa el cuento y extrae lecciones
6. **Síntesis de Aprendizaje:** Actualiza el perfil de estilo basado en críticas acumuladas

## 📊 Esquema de Base de Datos (SQLite)

```python
# SQLite es la base de datos por defecto (desarrollo)
# Modelos definidos en backend/models/database_sqlite.py

class Story(Base):
    __tablename__ = "stories"
    id = Column(String(36), primary_key=True)  # UUID como string
    title = Column(String(255))
    content = Column(Text, nullable=False)
    version = Column(Integer, default=1)
    is_seed = Column(Boolean, default=False)
    embedding_json = Column(JSON, nullable=True)  # Embedding como JSON
    created_at = Column(DateTime, default=datetime.utcnow)

class Critique(Base):
    __tablename__ = "critiques"
    id = Column(String(36), primary_key=True)
    story_id = Column(String(36), ForeignKey("stories.id", ondelete="CASCADE"))
    critique_text = Column(Text, nullable=False)
    score = Column(Integer)  # 1-10
    timestamp = Column(DateTime, default=datetime.utcnow)

class Lesson(Base):
    __tablename__ = "lessons"
    id = Column(String(36), primary_key=True)
    lesson_text = Column(Text, nullable=False)
    source_critique_id = Column(String(36), ForeignKey("critiques.id"))
    importance_score = Column(Integer, default=5)
    created_at = Column(DateTime, default=datetime.utcnow)

class Character(Base):
    __tablename__ = "characters"
    id = Column(String(36), primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    visual_details = Column(Text)
    personality_traits = Column(JSON)  # Lista de traits
    created_at = Column(DateTime, default=datetime.utcnow)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabla de evolución de estilo
CREATE TABLE style_evolution (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    version_label VARCHAR(50) NOT NULL,
    global_rules TEXT,
    active BOOLEAN DEFAULT true,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## 🚀 Instalación y Configuración

### 1. Preparar el Entorno

```bash
# Clonar el repositorio y navegar al directorio
cd CuentaCuentos

# Activar el entorno virtual
# En Windows:
.venv\Scripts\activate
# En Linux/Mac:
## 🚀 Inicio Rápido

### ⚠️ IMPORTANTE: Configuración de Seguridad

**Antes de empezar, lee [SECURITY.md](SECURITY.md)** para proteger tus claves de API.

**Resumen de seguridad:**
1. ✅ El archivo `backend/.env` está en `.gitignore` (no se sube a GitHub)
2. ✅ Usa `backend/.env.example` como plantilla
3. ❌ NUNCA subas tu archivo `.env` a repositorios públicos
4. 🔒 Ejecuta `.\audit-security.ps1` antes de hacer push

### 1. Instalar Dependencias

```powershell
# Navegar a la carpeta backend
cd backend

# Crear entorno virtual (si no existe)
python -m venv .venv

# Activar entorno virtual
.\.venv\Scripts\Activate.ps1  # Windows PowerShell
# o
source .venv/bin/activate      # Linux/Mac

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Configurar Variables de Entorno

**🔒 PASO CRÍTICO DE SEGURIDAD:**

```powershell
# 1. Copia el archivo de ejemplo
cd backend
Copy-Item .env.example .env

# 2. Edita el nuevo archivo .env con tu editor favorito
code .env  # o notepad .env
```

Añade tu **API key de Google Gemini**:

```env
# API Key de Google Gemini (REQUERIDO)
GEMINI_API_KEY=tu_api_key_real_aqui

# Base de Datos (SQLite por defecto)
DATABASE_URL=sqlite:///./cuentacuentos.db
```

**🔑 Obtén tu API key:** https://aistudio.google.com/app/apikey

**⚠️ IMPORTANTE:**
- El archivo `.env` contiene tu clave privada
- NUNCA compartas este archivo
- NUNCA lo subas a GitHub (ya está en `.gitignore`)
- Usa `.env.example` para compartir la estructura

### 3. Inicializar Base de Datos

La base de datos SQLite se crea automáticamente al iniciar la aplicación.

Para PostgreSQL (opcional):
```sql
CREATE DATABASE cuentacuentos_db;
\c cuentacuentos_db;
CREATE EXTENSION vector;
```

### 4. Ejecutar la Aplicación

**Opción 1: Script Automático (Recomendado)**

```powershell
# Desde la raíz del proyecto
.\iniciar.ps1
```

Este script:
- ✅ Verifica la estructura del proyecto
- ✅ Activa el entorno virtual automáticamente
- ✅ Inicializa la base de datos SQLite
- ✅ Inicia backend en puerto 8000
- ✅ Inicia frontend en puerto 3000
- ✅ Abre dos terminales separados

**Opción 2: Manual**

```bash
# Backend API (Terminal 1)
cd backend
.venv\Scripts\Activate.ps1  # Windows PowerShell
uvicorn main:app --reload --host 127.0.0.1 --port 8000

# Frontend Web (Terminal 2)
cd frontend
python -m http.server 3000
```

**URLs Disponibles:**
- **🎨 Generador:** http://localhost:3000/index.html
- **📚 Biblioteca:** http://localhost:3000/cuentos.html
- **🔌 API Backend:** http://localhost:8000
- **📋 API Docs:** http://localhost:8000/docs
- **💚 Health Check:** http://localhost:8000/health

**🎯 Nota**: Ambos servidores deben estar ejecutándose para funcionalidad completa (arquitectura API-first).

## 📋 API Endpoints Principales

### 🏃‍♂️ Health & Status
- `GET /` - Estado básico de la aplicación
- `GET /health` - Verificación detallada de salud

### 👥 Personajes
- `GET /characters` - Lista todos los personajes
- `GET /characters/{id}` - Detalles de un personaje específico

### 📖 Cuentos
- `POST /stories/prompt` - Genera un prompt basado en inputs del usuario
- `POST /stories` - Crea un nuevo cuento
- `GET /stories` - Lista cuentos (filtrable por `is_seed`)
- `GET /stories/{id}` - Obtiene un cuento específico

### 📝 Críticas
- `POST /critiques` - Añade una crítica a un cuento

## 🎯 Roadmap y Estado Actual

### ✅ Completado
- [x] Arquitectura modular API-first con backend/frontend separados
- [x] Sistema de persistencia de personajes con coherencia visual
- [x] Generación de prompts inteligente basada en guía de estilo
- [x] API REST completa con documentación automática
- [x] Modelos de datos para cuentos, críticas y evolución de estilo
- [x] Configuración centralizada y estructura escalable
- [x] **Integración completa con Google Gemini 2.5 Flash**
- [x] **Interfaz web completa (generador + biblioteca)**
- [x] **Migración a nuevo SDK de Gemini (google-genai)**
- [x] **Sistema de personajes con checkboxes opcionales**
- [x] **Navegación entre páginas (generador ↔ biblioteca)**

### 🔄 En Progreso
- [ ] Sistema de crítica automática (Function C: SelfCritique)
- [ ] Bucle de síntesis de aprendizaje (Function D: SynthesizeLearning)
- [ ] Paginación en biblioteca de cuentos

### 📅 Próximos Pasos
- [ ] Script de ingesta para cuentos semilla (60 cuentos base)
- [ ] Panel de observabilidad para monitorear evolución del estilo
- [ ] Sistema de tareas asíncronas para crítica en tiempo real
- [ ] Exportar cuentos (PDF/texto)
- [ ] Búsqueda y filtros en biblioteca

## 🎨 Ejemplo de Uso

### Desde la Interfaz Web

1. **Abrir generador:** http://localhost:3000/index.html
2. **Escribir tema:** "Un gatito pierde su pelota"
3. **(Opcional) Seleccionar personajes:** ☑ Martín - 4 años
4. **Click en "Generar Cuento ✨"**
5. **Ver el cuento generado** inmediatamente
6. **Ir a biblioteca** para ver todos los cuentos guardados

### Desde la API REST

```python
# Generar cuento automáticamente
POST /stories/generate
{
  "theme": "Una aventura en el bosque mágico",
  "character_names": ["Martín"],  # Opcional
  "moral_lesson": "La importancia de la amistad",  # Opcional
  "target_age": 6,  # Opcional (default: 6)
  "length": "medium",  # short, medium, long
  "special_elements": "Incluye animales que hablan"  # Opcional
}

# Listar cuentos guardados
GET /stories?limit=20

# Obtener cuento específico
GET /stories/{id}
```

## 🤝 Contribución

Este proyecto utiliza una arquitectura modular que facilita la contribución:

1. **Servicios:** Añadir nueva lógica de negocio en `/backend/services`
2. **Endpoints:** Nuevas rutas API en `/backend/routers`
3. **Modelos:** Esquemas de datos en `/backend/models`
4. **Configuración:** Variables centralizadas en `backend/config.py`

## 📊 Estado Actual del Proyecto

### ✅ Implementado y Funcionando

- **Backend API REST**
  - ✅ FastAPI con arquitectura modular
  - ✅ Google Gemini 2.5 Flash (SDK actualizado)
  - ✅ SQLite como base de datos por defecto
  - ✅ Embeddings con Gemini text-embedding-004
  - ✅ Gestión de personajes persistentes
  - ✅ Generación automática de cuentos
  - ✅ Sistema de prompts estructurados

- **Frontend Web**
  - ✅ Dos páginas separadas (generador + biblioteca)
  - ✅ Formulario flexible (solo tema obligatorio)
  - ✅ Selección múltiple de personajes
  - ✅ Visualización de cuentos guardados
  - ✅ Logs completos para debugging

- **Documentación**
  - ✅ README principal actualizado
  - ✅ Backend/README.md completo
  - ✅ Frontend/README.md detallado
  - ✅ Guía de migración de SDK (MIGRATION.md)
  - ✅ Documentación de código obsoleto

### 🚧 Pendiente de Implementar

- **Sistema de Aprendizaje Evolutivo**
  - ⏳ Crítica automática en background al crear cuentos
  - ⏳ Síntesis de lecciones cada N críticas
  - ⏳ Actualización del perfil de estilo
  - ⏳ RAG con búsqueda por similitud de embeddings

- **Mejoras del Frontend**
  - ⏳ Búsqueda y filtrado en biblioteca
  - ⏳ Paginación de cuentos
  - ⏳ Exportación a PDF/TXT
  - ⏳ Modo oscuro

## 📚 Documentación Adicional

- 📖 [Documentación del Backend](backend/README.md)
- 📖 [Documentación del Frontend](frontend/README.md)
- 🔒 [Guía de Seguridad](SECURITY.md) - **Lectura obligatoria antes de subir a GitHub**
- 🏗️ [Arquitectura del Sistema](docs/ARCHITECTURE.md)

## 🔒 Seguridad y Buenas Prácticas

### Antes de Subir a GitHub

**EJECUTA SIEMPRE:**
```powershell
.\audit-security.ps1
```

Este script verifica:
- ✅ `.env` está ignorado por git
- ✅ No hay claves de API expuestas en código
- ✅ No hay bases de datos en staging
- ✅ `.env.example` no contiene claves reales
- ✅ Archivos sensibles protegidos

### Archivos Protegidos

Estos archivos **NUNCA** se suben a GitHub:
- 🔒 `backend/.env` - Contiene tu API key
- 🔒 `backend/*.db` - Bases de datos SQLite
- 🔒 `backend/.venv/` - Entorno virtual Python
- 🔒 `backend/__pycache__/` - Archivos compilados

### ¿Qué SÍ se sube?

- ✅ Código fuente (.py, .js, .html, .css)
- ✅ Documentación (.md)
- ✅ Configuración de ejemplo (.env.example)
- ✅ Dependencias (requirements.txt)
- ✅ Scripts de utilidad (.ps1)

**📖 Más detalles:** Lee [SECURITY.md](SECURITY.md) para una guía completa.
- 📖 [Guía de Migración Gemini SDK](backend/MIGRATION.md)
- 📖 [Estado del Proyecto](PROJECT_STATUS.md)
- 📖 [Solución de Errores](SOLUCION-ERRORES.md)
- 📖 [Informe de Limpieza](RESUMEN-LIMPIEZA.md)

## 📄 Licencia

[Especificar licencia según necesidades del proyecto]
    actionable_lesson TEXT
);
---

## 📚 Documentación por Componente

- **[Backend README](backend/README.md)** - API REST, endpoints, configuración del servidor
- **[Frontend README](frontend/README.md)** ✨ - Interfaz web, páginas, navegación entre vistas
- **[MIGRATION.md](backend/MIGRATION.md)** - Migración del SDK de Gemini
- **[PROJECT_STATUS.md](PROJECT_STATUS.md)** - Estado y roadmap del proyecto

---

**Desarrollado con ❤️ usando FastAPI y Google Gemini**

