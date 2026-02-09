from datetime import datetime, timedelta, timezone
from typing import Optional
import secrets
import jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from models import schemas, database_sqlite
from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

# Configuración de Passlib para el hasheo de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Constantes
PASSWORD_RESET_TOKEN_EXPIRE_HOURS = 1


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica si una contraseña en texto plano coincide con un hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Genera el hash de una contraseña."""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Crea un nuevo token de acceso JWT.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    
    # Asegurarse de que SECRET_KEY no sea None
    if not SECRET_KEY:
        raise ValueError("La SECRET_KEY no está configurada en el entorno.")
        
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def generate_reset_token() -> str:
    """
    Genera un token seguro y único para reset de contraseña.
    """
    return secrets.token_urlsafe(32)


def create_password_reset_token(db: Session, user_id: int) -> str:
    """
    Crea un token de reset de contraseña para un usuario.
    
    Args:
        db: Sesión de base de datos
        user_id: ID del usuario
        
    Returns:
        str: Token generado
    """
    token = generate_reset_token()
    expires_at = datetime.utcnow() + timedelta(hours=PASSWORD_RESET_TOKEN_EXPIRE_HOURS)
    
    database_sqlite.create_password_reset_token(db, user_id, token, expires_at)
    
    return token


def validate_reset_token(db: Session, token: str) -> Optional[int]:
    """
    Valida un token de reset de contraseña y devuelve el user_id si es válido.
    
    Args:
        db: Sesión de base de datos
        token: Token a validar
        
    Returns:
        Optional[int]: ID del usuario si el token es válido, None si no lo es
    """
    reset_token = database_sqlite.get_password_reset_token(db, token)
    
    if not reset_token:
        return None
        
    # Verificar expiración
    if reset_token.expires_at < datetime.utcnow():
        return None
        
    return reset_token.user_id


def reset_password(db: Session, token: str, new_password: str) -> bool:
    """
    Resetea la contraseña de un usuario usando un token válido.
    
    Args:
        db: Sesión de base de datos
        token: Token de reset
        new_password: Nueva contraseña
        
    Returns:
        bool: True si el reset fue exitoso, False en caso contrario
    """
    # Validar token
    user_id = validate_reset_token(db, token)
    if not user_id:
        return False
    
    # Actualizar contraseña
    new_hashed_password = get_password_hash(new_password)
    user = database_sqlite.update_user_password(db, user_id, new_hashed_password)
    
    if not user:
        return False
    
    # Marcar token como usado
    reset_token = database_sqlite.get_password_reset_token(db, token)
    if reset_token:
        database_sqlite.mark_token_as_used(db, reset_token.id)
    
    return True


def change_password(db: Session, user_id: int, current_password: str, new_password: str) -> bool:
    """
    Cambia la contraseña de un usuario verificando la contraseña actual.
    
    Args:
        db: Sesión de base de datos
        user_id: ID del usuario
        current_password: Contraseña actual
        new_password: Nueva contraseña
        
    Returns:
        bool: True si el cambio fue exitoso, False en caso contrario
    """
    # Obtener usuario
    user = database_sqlite.get_user_by_id(db, user_id)
    if not user:
        return False
    
    # Verificar contraseña actual
    if not verify_password(current_password, user.hashed_password):
        return False
    
    # Actualizar contraseña
    new_hashed_password = get_password_hash(new_password)
    updated_user = database_sqlite.update_user_password(db, user_id, new_hashed_password)
    
    return updated_user is not None
