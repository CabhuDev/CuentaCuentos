# Modelos Pydantic (API Data Contracts)
import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class StoryPromptInput(BaseModel):
    """Schema para generación de prompts (formato legacy)"""
    personaje: str
    personaje_id: Optional[str] = None
    rol_personaje: Optional[str] = None
    contexto_opcional: Optional[str] = None
    emocion_objetivo: Optional[str] = None
    lugar: Optional[str] = None
    objeto_significativo: Optional[str] = None
    personajes_secundarios: Optional[List[str]] = None


class StoryGenerateInput(BaseModel):
    theme: str = Field(..., description="Tema principal del cuento")
    character_names: Optional[List[str]] = Field(None, description="Lista de nombres de personajes (opcional)")
    moral_lesson: Optional[str] = Field(None, description="Lección moral opcional")
    target_age: Optional[int] = Field(6, ge=3, le=12, description="Edad objetivo del niño")
    length: str = Field("medium", description="Longitud del cuento: short, medium, long")
    special_elements: Optional[str] = Field(None, description="Elementos especiales opcionales")


class StoryBase(BaseModel):
    title: str
    content: str


class StoryCreate(StoryBase):
    is_seed: bool = False
    prompt_inputs: Optional[StoryPromptInput] = None


class StoryResponse(StoryBase):
    id: uuid.UUID
    version: int
    is_seed: bool
    illustration_template: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True


class StoryResponseWithPrompt(StoryResponse):
    prompt_used: Optional[str] = None


class StoryPromptResponse(BaseModel):
    prompt: str


class CritiqueBase(BaseModel):
    score_coherence: int = Field(..., gt=0, le=10)
    score_style: int = Field(..., gt=0, le=10)
    strengths: List[str]
    weaknesses: List[str]
    improvement_advice: str


class CritiqueCreate(CritiqueBase):
    story_id: uuid.UUID


class CritiqueResponse(CritiqueBase):
    id: uuid.UUID
    story_id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True


class CharacterDetail(BaseModel):
    id: str
    nombre: str
    estado: str
    rasgos_distintivos: Dict[str, Any]
    armario_coherente: Dict[str, Any]
    personalidad_narrativa: Dict[str, Any]
    reglas_ilustracion: Dict[str, Any]
    accesorios_frecuentes: Optional[List[Dict[str, Any]]] = None
    historico_apariciones: Optional[List[Dict[str, Any]]] = None
    metadata: Optional[Dict[str, Any]] = None


class CharacterResponse(BaseModel):
    id: str
    nombre: str
    estado: str
    edad_aparente: Optional[str] = None
    prompt_base_ia: Optional[str] = None
    total_apariciones: Optional[int] = None


# === SCHEMAS DE AUDIO ===

class AudioGenerationRequest(BaseModel):
    """Schema para solicitud de generación de audio"""
    texto: str = Field(..., description="Texto del cuento a narrar")
    cuento_id: Optional[str] = Field(None, description="ID del cuento (opcional)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "texto": "Había una vez en un bosque encantado...",
                "cuento_id": "cuento_123"
            }
        }


class AudioGenerationResponse(BaseModel):
    """Schema para respuesta de generación de audio"""
    success: bool = Field(..., description="Indica si la generación fue exitosa")
    audio_url: Optional[str] = Field(None, description="URL del archivo de audio generado")
    message: str = Field(..., description="Mensaje descriptivo del resultado")
    file_path: Optional[str] = Field(None, description="Ruta del archivo en el servidor")
    duration: Optional[float] = Field(None, description="Duración del audio en segundos (estimada)")
    characters_used: Optional[int] = Field(None, description="Caracteres utilizados del texto")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "audio_url": "/static/audio/cuento_123.mp3",
                "message": "Audio generado exitosamente",
                "file_path": "data/audio/cuento_123.mp3",
                "duration": 45.5,
                "characters_used": 250
            }
        }


class VoiceInfo(BaseModel):
    """Schema para información de voz disponible"""
    voice_id: str = Field(..., description="ID único de la voz")
    name: str = Field(..., description="Nombre de la voz")
    category: Optional[str] = Field(None, description="Categoría de la voz")
    description: Optional[str] = Field(None, description="Descripción de la voz")
    preview_url: Optional[str] = Field(None, description="URL de previsualización")
    labels: Optional[Dict[str, Any]] = Field(None, description="Etiquetas adicionales")
    
    class Config:
        json_schema_extra = {
            "example": {
                "voice_id": "JBFqnCBsd6RMkjVDRZzb",
                "name": "George",
                "category": "premade",
                "description": "Warm, Captivating Storyteller",
                "labels": {"accent": "american", "age": "middle-aged"}
            }
        }


class VoicesListResponse(BaseModel):
    """Schema para respuesta de lista de voces"""
    voices: List[VoiceInfo] = Field(..., description="Lista de voces disponibles")
    total: int = Field(..., description="Total de voces disponibles")
    
    class Config:
        json_schema_extra = {
            "example": {
                "voices": [],
                "total": 21
            }
        }


# === SCHEMAS DE AUTENTICACIÓN ===

class UserBase(BaseModel):
    username: str


class UserInDB(UserBase):
    hashed_password: str


class UserCreate(UserBase):
    password: str
    email: Optional[str] = None  # Email opcional para reset de contraseña


class User(UserBase):
    id: int
    email: Optional[str] = None

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


# === SCHEMAS PARA RESET Y CAMBIO DE CONTRASEÑA ===

class ForgotPasswordRequest(BaseModel):
    """Schema para solicitar reset de contraseña"""
    email: str = Field(..., description="Email del usuario")
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "usuario@ejemplo.com"
            }
        }


class ResetPasswordRequest(BaseModel):
    """Schema para resetear contraseña con token"""
    token: str = Field(..., description="Token de reset recibido por email")
    new_password: str = Field(..., min_length=6, description="Nueva contraseña")
    
    class Config:
        json_schema_extra = {
            "example": {
                "token": "abc123...",
                "new_password": "nuevaContraseña123"
            }
        }


class ChangePasswordRequest(BaseModel):
    """Schema para cambiar contraseña conociendo la actual"""
    current_password: str = Field(..., description="Contraseña actual")
    new_password: str = Field(..., min_length=6, description="Nueva contraseña")
    
    class Config:
        json_schema_extra = {
            "example": {
                "current_password": "contraseñaActual123",
                "new_password": "nuevaContraseña123"
            }
        }


class PasswordResetResponse(BaseModel):
    """Schema para respuesta de operaciones de contraseña"""
    success: bool = Field(..., description="Indica si la operación fue exitosa")
    message: str = Field(..., description="Mensaje descriptivo")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Contraseña actualizada exitosamente"
            }
        }
