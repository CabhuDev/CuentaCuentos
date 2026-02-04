# Modelos de base de datos compatibles con SQLite
# Versión simplificada sin pgvector para desarrollo local

import os
import uuid
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Text,
    Boolean,
    DateTime,
    ForeignKey,
    JSON,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Cargar variables de entorno PRIMERO
load_dotenv()

# --- Database Configuration ---
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./cuentacuentos.db")

# Configuración específica para SQLite
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# --- SQLAlchemy Models (SQLite Compatible) ---


class Story(Base):
    """Tabla Maestra de Cuentos"""

    __tablename__ = "stories"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(255))
    content = Column(Text, nullable=False)
    version = Column(Integer, default=1)
    is_seed = Column(Boolean, default=False)
    # En SQLite guardamos el embedding como JSON en lugar de Vector
    embedding_json = Column(JSON, nullable=True)
    # Plantilla para generación de ilustraciones con IA
    illustration_template = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class Critique(Base):
    """Tabla de Críticas Generadas por Gemini"""

    __tablename__ = "critiques"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    story_id = Column(String(36), ForeignKey("stories.id", ondelete="CASCADE"))
    critique_text = Column(Text, nullable=False)
    score = Column(Integer)  # 1-10
    timestamp = Column(DateTime, default=datetime.utcnow)


class Lesson(Base):
    """Tabla de Lecciones Sintetizadas"""

    __tablename__ = "lessons"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    lesson_text = Column(Text, nullable=False)
    source_critique_id = Column(
        String(36), ForeignKey("critiques.id", ondelete="SET NULL"), nullable=True
    )
    importance_score = Column(Integer, default=5)
    created_at = Column(DateTime, default=datetime.utcnow)


class Character(Base):
    """Tabla de Personajes Persistentes"""

    __tablename__ = "characters"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    visual_details = Column(Text)
    personality_traits = Column(JSON)  # Lista de strings
    created_at = Column(DateTime, default=datetime.utcnow)


# --- Dependency Injection para FastAPI ---
def get_db():
    """Genera una sesión de base de datos para cada request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Inicializa la base de datos creando todas las tablas."""
    Base.metadata.create_all(bind=engine)
    print("✅ Base de datos SQLite inicializada correctamente")
