# Modelos de base de datos (SQLAlchemy)
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
from sqlalchemy.sql import func, text
from pgvector.sqlalchemy import Vector
from config import DATABASE_URL

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Story(Base):
    """Tabla Maestra de Cuentos"""

    __tablename__ = "stories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255))
    content = Column(Text, nullable=False)
    version = Column(Integer, default=1)
    is_seed = Column(Boolean, default=False)
    embedding = Column(Vector(768))
    created_at = Column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )


class Critique(Base):
    """Tabla de Críticas"""

    __tablename__ = "critiques"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    story_id = Column(
        UUID(as_uuid=True), ForeignKey("stories.id", ondelete="CASCADE"), nullable=False
    )
    score_coherence = Column(Integer)
    score_style = Column(Integer)
    strengths = Column(ARRAY(Text))
    weaknesses = Column(ARRAY(Text))
    improvement_advice = Column(Text)
    created_at = Column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )


class StyleEvolution(Base):
    """Tabla de Contexto Evolutivo"""

    __tablename__ = "style_evolution"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    version_label = Column(String(50), nullable=False)
    global_rules = Column(Text)
    active = Column(Boolean, default=True)
    updated_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


def get_db():
    """Generador de sesión de base de datos"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Crear todas las tablas en la base de datos"""
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        conn.commit()

    Base.metadata.create_all(bind=engine)
    print("Tablas creadas en la base de datos.")