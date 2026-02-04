# Router para endpoints de personajes
from typing import List
from fastapi import APIRouter, HTTPException, status
from models.schemas import CharacterDetail, CharacterResponse
from services.character_service import character_service

router = APIRouter(prefix="/characters", tags=["Characters"])


@router.get(
    "",
    response_model=List[CharacterResponse],
    summary="Listar todos los personajes",
)
def list_characters():
    """Obtiene la lista de todos los personajes registrados."""
    characters = character_service.get_all_characters()
    return [
        CharacterResponse(
            id=char.get("id", ""),
            nombre=char.get("nombre", ""),
            estado=char.get("estado", "activo"),
            edad_aparente=char.get("rasgos_distintivos", {}).get("edad_aparente"),
            prompt_base_ia=char.get("reglas_ilustracion", {}).get("prompt_base_ia"),
            total_apariciones=char.get("metadata", {}).get("total_apariciones", 0),
        )
        for char in characters
    ]


@router.get(
    "/{character_id}",
    response_model=CharacterDetail,
    summary="Obtener detalles de un personaje",
)
def get_character(character_id: str):
    """Obtiene los detalles completos de un personaje específico."""
    character = character_service.get_character_by_id(character_id)
    
    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Personaje con id '{character_id}' no encontrado.",
        )
    
    return CharacterDetail(**character)