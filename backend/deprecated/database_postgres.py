import os
import uuid
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Text,
    Boolean,
    TIMESTAMP,
    ForeignKey,
)
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector

# --- Database Configuration ---
# En una aplicación real, esto vendría de variables de entorno.
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://user:password@localhost/cuentacuentos_db"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# --- SQLAlchemy Models ---
# Estas clases son la traducción directa de tu esquema SQL a código Python.


class Story(Base):
    """Tabla Maestra de Cuentos"""

    __tablename__ = "stories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255))
    content = Column(Text, nullable=False)
    version = Column(Integer, default=1)
    is_seed = Column(Boolean, default=False)  # True para tus 60 originales
    embedding = Column(Vector(768))  # Gemini embedding size
    created_at = Column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )


class Critique(Base):
    """Tabla de Críticas (El motor de aprendizaje)"""

    __tablename__ = "critiques"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    story_id = Column(
        UUID(as_uuid=True), ForeignKey("stories.id", ondelete="CASCADE"), nullable=False
    )
    score_coherence = Column(Integer)  # CHECK constraint se define en la DB
    score_style = Column(Integer)  # CHECK constraint se define en la DB
    strengths = Column(ARRAY(Text))
    weaknesses = Column(ARRAY(Text))
    improvement_advice = Column(Text)
    created_at = Column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )


class StyleEvolution(Base):
    """Tabla de Contexto Evolutivo (El "Cerebro" de la Gem)"""

    __tablename__ = "style_evolution"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    version_label = Column(String(50), nullable=False)
    global_rules = Column(Text)  # Reglas consolidadas
    active = Column(Boolean, default=True)
    updated_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


# --- Dependency for FastAPI ---
def get_db():
    """
    Generador de sesión de base de datos para usar como dependencia en FastAPI.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """
    Función para crear todas las tablas en la base de datos.
    Solo se necesita ejecutar una vez.
    """
    # En PostgreSQL, la extensión debe ser creada por un superusuario.
    # Conexión cruda para crear la extensión si no existe.
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        conn.commit()

    Base.metadata.create_all(bind=engine)
    print("Tablas creadas en la base de datos.")

