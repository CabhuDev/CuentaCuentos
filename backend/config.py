# Configuración centralizada
import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Rutas base
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"

# Database - Por defecto usa SQLite (no requiere PostgreSQL)
DATABASE_URL = os.getenv(
    "DATABASE_URL", "sqlite:///./cuentacuentos.db"
)

# Paths para archivos JSON
STYLE_GUIDE_PATH = DATA_DIR / "style_guide.json"
CHARACTERS_PATH = DATA_DIR / "characters.json"
STYLE_PROFILE_PATH = DATA_DIR / "style_profile.json"
LEARNING_HISTORY_PATH = DATA_DIR / "learning_history.json"

# API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# ElevenLabs Configuration
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")
ELEVENLABS_MODEL_ID = os.getenv("ELEVENLABS_MODEL_ID", "eleven_multilingual_v2")

# Configuración de la app
APP_TITLE = "CuentaCuentos AI Engine"
APP_DESCRIPTION = "API para la generación y mejora evolutiva de cuentos infantiles."
APP_VERSION = "0.1.0"


# Configuración de Autenticación (JWT)
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
