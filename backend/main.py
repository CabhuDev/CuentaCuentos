# Aplicación FastAPI principal - API REST pura para arquitectura frontend independiente
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import APP_TITLE, APP_DESCRIPTION, APP_VERSION
from routers import stories, characters, critiques, learning
from services.character_service import character_service
from services.prompt_service import prompt_service
from services.gemini_service import gemini_service

app = FastAPI(
    title=APP_TITLE,
    description=APP_DESCRIPTION,
    version=APP_VERSION,
)

# CORS para permitir acceso del frontend independiente
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción: especificar dominios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(stories.router)
app.include_router(characters.router)
app.include_router(critiques.router)
app.include_router(learning.router)


@app.on_event("startup")
def on_startup():
    """Inicialización de la aplicación"""
    # Pre-cargar datos en memoria para mejor rendimiento
    character_service.load_characters()
    prompt_service.load_style_guide()
    
    # Inicializar base de datos (crea las tablas si no existen)
    from models.database_sqlite import init_db
    init_db()


@app.get("/", tags=["Health"])
def root():
    """Endpoint de salud básico para API REST pura"""
    return {
        "message": "🌟 CuentaCuentos AI API está funcionando!",
        "status": "healthy",
        "api_docs": "/docs",
        "version": APP_VERSION,
        "frontend": "Aplicación independiente en /frontend/"
    }


@app.get("/health", tags=["Health"])
def health_check():
    """Endpoint de verificación de salud más detallado"""
    try:
        characters_loaded = len(character_service.load_characters())
        style_guide_loaded = bool(prompt_service.load_style_guide())
        gemini_configured = gemini_service.is_configured()
        
        return {
            "status": "healthy",
            "characters_loaded": characters_loaded,
            "style_guide_loaded": style_guide_loaded,
            "gemini_configured": gemini_configured,
            "version": APP_VERSION,
            "architecture": "API-first con frontend independiente"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "version": APP_VERSION
        }