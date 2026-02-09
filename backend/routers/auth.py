from datetime import timedelta
from typing import List

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from models import database_sqlite, schemas
from services import auth_service
from config import ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter(
    tags=["Authentication"],
)

# Este esquema le dice a FastAPI dónde buscar el token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database_sqlite.get_db)):
    """
    Decodifica el token JWT para obtener el usuario actual.
    Esta es la dependencia principal de seguridad.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, auth_service.SECRET_KEY, algorithms=[auth_service.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="El token ha expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.PyJWTError:
        raise credentials_exception
        
    user = database_sqlite.get_user_by_username(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: schemas.User = Depends(get_current_user)):
    """
    Verifica si el usuario obtenido del token está activo.
    (Actualmente es un placeholder, se puede extender para usuarios deshabilitados).
    """
    # En el futuro, podrías verificar un campo `disabled` en el usuario.
    # if current_user.disabled:
    #     raise HTTPException(status_code=400, detail="Usuario inactivo")
    return current_user


@router.post("/token", response_model=schemas.Token)
async def login_for_access_token(db: Session = Depends(database_sqlite.get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Endpoint de login. Recibe usuario y contraseña, devuelve un token de acceso.
    """
    user = database_sqlite.get_user_by_username(db, username=form_data.username)
    if not user or not auth_service.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nombre de usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth_service.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(database_sqlite.get_db)):
    """
    Endpoint para registrar un nuevo usuario.
    Envía automáticamente un email de bienvenida si se proporciona email.
    """
    from services import email_service
    
    db_user = database_sqlite.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="El nombre de usuario ya está registrado")
    
    hashed_password = auth_service.get_password_hash(user.password)
    new_user = database_sqlite.create_user(db=db, user=user, hashed_password=hashed_password)
    
    # Enviar email de bienvenida si el usuario proporcionó email
    if user.email:
        try:
            email_service.send_welcome_email(
                email=user.email,
                username=user.username
            )
        except Exception as e:
            # No fallar el registro si falla el email
            print(f"⚠️ Error al enviar email de bienvenida: {str(e)}")
    
    return new_user


@router.get("/users/me", response_model=schemas.User)
async def read_users_me(current_user: schemas.User = Depends(get_current_active_user)):
    """
    Endpoint protegido que devuelve la información del usuario autenticado actualmente.
    """
    return current_user


@router.post("/forgot-password", response_model=schemas.PasswordResetResponse)
async def forgot_password(
    request: schemas.ForgotPasswordRequest,
    db: Session = Depends(database_sqlite.get_db)
):
    """
    Endpoint para solicitar el reset de contraseña.
    Envía un email con un token de reset si el email está registrado.
    """
    from services import email_service
    
    # Buscar usuario por email
    user = database_sqlite.get_user_by_email(db, email=request.email)
    
    # Por seguridad, siempre devuelve el mismo mensaje incluso si el email no existe
    if not user:
        return schemas.PasswordResetResponse(
            success=True,
            message="Si el email está registrado, recibirás un enlace de recuperación en breve"
        )
    
    # Generar token de reset
    reset_token = auth_service.create_password_reset_token(db, user.id)
    
    # Enviar email
    email_sent = email_service.send_password_reset_email(
        email=user.email,
        username=user.username,
        reset_token=reset_token
    )
    
    # Limpiar tokens expirados (tareas de mantenimiento)
    database_sqlite.delete_expired_tokens(db)
    
    return schemas.PasswordResetResponse(
        success=True,
        message="Si el email está registrado, recibirás un enlace de recuperación en breve"
    )


@router.post("/reset-password", response_model=schemas.PasswordResetResponse)
async def reset_password(
    request: schemas.ResetPasswordRequest,
    db: Session = Depends(database_sqlite.get_db)
):
    """
    Endpoint para resetear la contraseña usando un token válido.
    """
    from services import email_service
    
    # Intentar resetear contraseña
    success = auth_service.reset_password(db, request.token, request.new_password)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token inválido o expirado"
        )
    
    # Obtener usuario para enviar email de confirmación
    user_id = auth_service.validate_reset_token(db, request.token)
    if user_id:
        user = database_sqlite.get_user_by_id(db, user_id)
        if user and user.email:
            email_service.send_password_changed_confirmation(
                email=user.email,
                username=user.username
            )
    
    return schemas.PasswordResetResponse(
        success=True,
        message="Contraseña actualizada exitosamente"
    )


@router.post("/change-password", response_model=schemas.PasswordResetResponse)
async def change_password(
    request: schemas.ChangePasswordRequest,
    current_user: schemas.User = Depends(get_current_active_user),
    db: Session = Depends(database_sqlite.get_db)
):
    """
    Endpoint para cambiar la contraseña conociendo la contraseña actual.
    Requiere autenticación.
    """
    from services import email_service
    
    # Intentar cambiar contraseña
    success = auth_service.change_password(
        db,
        current_user.id,
        request.current_password,
        request.new_password
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Contraseña actual incorrecta"
        )
    
    # Enviar email de confirmación si el usuario tiene email
    if current_user.email:
        email_service.send_password_changed_confirmation(
            email=current_user.email,
            username=current_user.username
        )
    
    return schemas.PasswordResetResponse(
        success=True,
        message="Contraseña cambiada exitosamente"
    )
