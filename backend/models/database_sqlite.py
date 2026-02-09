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


class User(Base):
    """Tabla de Usuarios para Autenticación"""
    
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=True)  # Para reset de contraseña
    hashed_password = Column(String, nullable=False)


class PasswordResetToken(Base):
    """Tabla de Tokens para Reset de Contraseña"""
    
    __tablename__ = "password_reset_tokens"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token = Column(String(255), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    used = Column(Boolean, default=False, nullable=False)


# --- Funciones CRUD para Usuarios ---

def get_user_by_username(db: "Session", username: str):
    """Obtiene un usuario por su nombre de usuario."""
    from . import schemas  # Importación local para evitar ciclo
    return db.query(User).filter(User.username == username).first()


def get_user_by_email(db: "Session", email: str):
    """Obtiene un usuario por su email."""
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: "Session", user_id: int):
    """Obtiene un usuario por su ID."""
    return db.query(User).filter(User.id == user_id).first()


def create_user(db: "Session", user: "schemas.UserCreate", hashed_password: str):
    """Crea un nuevo usuario en la base de datos."""
    from . import schemas # Importación local
    db_user = User(username=user.username, email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user_password(db: "Session", user_id: int, new_hashed_password: str):
    """Actualiza la contraseña de un usuario."""
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.hashed_password = new_hashed_password
        db.commit()
        db.refresh(user)
    return user


# --- Funciones CRUD para Tokens de Reset de Contraseña ---

def create_password_reset_token(db: "Session", user_id: int, token: str, expires_at: datetime):
    """Crea un nuevo token de reset de contraseña."""
    reset_token = PasswordResetToken(
        user_id=user_id,
        token=token,
        expires_at=expires_at
    )
    db.add(reset_token)
    db.commit()
    db.refresh(reset_token)
    return reset_token


def get_password_reset_token(db: "Session", token: str):
    """Obtiene un token de reset por su valor."""
    return db.query(PasswordResetToken).filter(
        PasswordResetToken.token == token,
        PasswordResetToken.used == False
    ).first()


def mark_token_as_used(db: "Session", token_id: str):
    """Marca un token como usado."""
    token = db.query(PasswordResetToken).filter(PasswordResetToken.id == token_id).first()
    if token:
        token.used = True
        db.commit()
        db.refresh(token)
    return token


def delete_expired_tokens(db: "Session"):
    """Elimina tokens expirados de la base de datos."""
    now = datetime.utcnow()
    db.query(PasswordResetToken).filter(PasswordResetToken.expires_at < now).delete()
    db.commit()


# --- Dependency Injection para FastAPI ---
def get_db():
    """Genera una sesión de base de datos para cada request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _run_migrations():
    """Ejecuta migraciones manuales para columnas añadidas a tablas existentes."""
    import sqlite3
    
    # Obtener ruta de la BD desde la URL
    db_path = DATABASE_URL.replace("sqlite:///", "")
    if not os.path.exists(db_path):
        return  # La BD se creará desde cero con create_all
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Migraciones pendientes
    migrations = [
        # (tabla, columna, sentencias SQL)
        ("users", "email", [
            "ALTER TABLE users ADD COLUMN email VARCHAR",
            "CREATE UNIQUE INDEX IF NOT EXISTS ix_users_email ON users(email)",
        ]),
    ]
    
    for table, column, sql_statements in migrations:
        try:
            cursor.execute(f"PRAGMA table_info({table})")
            columns = [row[1] for row in cursor.fetchall()]
            if column not in columns:
                for sql in sql_statements:
                    cursor.execute(sql)
                print(f"  🔄 Migración: Añadida columna '{column}' a tabla '{table}'")
        except Exception as e:
            print(f"  ⚠️ Error en migración ({table}.{column}): {e}")
    
    conn.commit()
    conn.close()


def init_db():
    """Inicializa la base de datos creando todas las tablas y ejecutando migraciones."""
    _run_migrations()
    Base.metadata.create_all(bind=engine)
    print("✅ Base de datos SQLite inicializada correctamente")
