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