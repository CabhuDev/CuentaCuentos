"""
Router para endpoints de generación de audio con ElevenLabs.
Proporciona funcionalidad de text-to-speech para narración de cuentos.
"""
from fastapi import APIRouter, HTTPException, Path
from fastapi.responses import JSONResponse
from typing import Dict, Any
import uuid
import logging

from models.schemas import (
    AudioGenerationRequest,
    AudioGenerationResponse,
    VoiceInfo,
    VoicesListResponse
)
from services.audio_service import audio_service
from config import ELEVENLABS_VOICE_ID

# Configurar logging
logger = logging.getLogger(__name__)

# Crear router
router = APIRouter(
    prefix="/audio",
    tags=["Audio"],
    responses={404: {"description": "No encontrado"}},
)


@router.post(
    "/cuentos/{cuento_id}/generar",
    response_model=AudioGenerationResponse,
    summary="Generar audio para un cuento",
    description="Genera narración en audio del texto del cuento usando ElevenLabs TTS"
)
async def generar_audio_cuento(
    cuento_id: str = Path(..., description="ID del cuento"),
    request: AudioGenerationRequest = None
) -> AudioGenerationResponse:
    """
    Genera archivo de audio MP3 narrando el texto del cuento.
    
    Args:
        cuento_id: Identificador único del cuento
        request: Datos de la solicitud con el texto a narrar
        
    Returns:
        AudioGenerationResponse con URL del audio generado
        
    Raises:
        HTTPException: Si ocurre un error en la generación
    """
    try:
        logger.info(f"Generando audio para cuento {cuento_id}")
        
        # Validar que se envió el texto
        if not request or not request.texto:
            raise HTTPException(
                status_code=400,
                detail="El campo 'texto' es requerido para generar el audio"
            )
        
        # Validar longitud del texto
        if len(request.texto) < 10:
            raise HTTPException(
                status_code=400,
                detail="El texto debe tener al menos 10 caracteres"
            )
        
        # Advertencia si el texto es muy largo (más de 1500 caracteres con plan gratuito)
        char_count = len(request.texto)
        if char_count > 1500:
            logger.warning(f"Texto largo detectado: {char_count} caracteres. Puede exceder cuota gratuita.")
        
        # Generar el audio usando el servicio
        file_path = audio_service.generar_audio_cuento(
            cuento_id=cuento_id,
            texto=request.texto
        )
        
        # Construir URL pública del archivo
        audio_url = f"/data/audio/{cuento_id}.mp3"
        
        # Calcular caracteres utilizados
        characters_used = len(request.texto)
        
        # Estimar duración (aproximadamente 150 palabras por minuto = 2.5 palabras/segundo)
        palabras = len(request.texto.split())
        duration_estimate = palabras / 2.5
        
        logger.info(f"Audio generado exitosamente: {file_path}")
        
        return AudioGenerationResponse(
            success=True,
            audio_url=audio_url,
            message="Audio generado exitosamente",
            file_path=file_path,
            duration=round(duration_estimate, 2),
            characters_used=characters_used
        )
    
    except HTTPException:
        # Re-lanzar excepciones HTTP sin modificar
        raise
        
    except ValueError as ve:
        # Errores de validación del servicio
        logger.error(f"Error de validación: {str(ve)}")
        raise HTTPException(status_code=400, detail=str(ve))
        
    except PermissionError as pe:
        # Errores de permisos de API
        logger.error(f"Error de permisos: {str(pe)}")
        raise HTTPException(
            status_code=403,
            detail=f"Error de permisos en ElevenLabs API: {str(pe)}"
        )
        
    except Exception as e:
        # Otros errores
        logger.error(f"Error generando audio: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error al generar el audio: {str(e)}"
        )


@router.delete(
    "/cuentos/{cuento_id}",
    summary="Eliminar audio de un cuento",
    description="Elimina el archivo de audio asociado a un cuento"
)
async def eliminar_audio_cuento(
    cuento_id: str = Path(..., description="ID del cuento")
) -> Dict[str, Any]:
    """
    Elimina el archivo de audio MP3 del cuento especificado.
    
    Args:
        cuento_id: Identificador único del cuento
        
    Returns:
        Diccionario con el resultado de la operación
        
    Raises:
        HTTPException: Si el archivo no existe o hay un error al eliminar
    """
    try:
        logger.info(f"Eliminando audio para cuento {cuento_id}")
        
        # Verificar si el audio existe
        if not audio_service.audio_existe(cuento_id):
            raise HTTPException(
                status_code=404,
                detail=f"No existe audio para el cuento {cuento_id}"
            )
        
        # Eliminar el archivo
        audio_service.eliminar_audio(cuento_id)
        
        logger.info(f"Audio eliminado exitosamente: {cuento_id}")
        
        return {
            "success": True,
            "message": f"Audio del cuento {cuento_id} eliminado exitosamente"
        }
        
    except HTTPException:
        # Re-lanzar excepciones HTTP
        raise
        
    except Exception as e:
        logger.error(f"Error eliminando audio: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error al eliminar el audio: {str(e)}"
        )


@router.get(
    "/voces",
    response_model=VoicesListResponse,
    summary="Listar voces disponibles",
    description="Obtiene la lista de voces disponibles en ElevenLabs para narración"
)
async def obtener_voces_disponibles() -> VoicesListResponse:
    """
    Obtiene todas las voces disponibles en la cuenta de ElevenLabs.
    
    Returns:
        VoicesListResponse con la lista de voces y metadata
        
    Raises:
        HTTPException: Si hay un error al obtener las voces
    """
    try:
        logger.info("Obteniendo lista de voces disponibles")
        
        # Obtener voces del servicio (retorna diccionarios)
        voces_raw = audio_service.obtener_voces_disponibles()
        
        # Convertir a modelos Pydantic
        voces = []
        for voz in voces_raw:
            voice_info = VoiceInfo(
                voice_id=voz.get("voice_id", ""),
                name=voz.get("name", "Unknown"),
                category=voz.get("category"),
                description=voz.get("description"),
                preview_url=voz.get("preview_url"),
                labels=voz.get("labels")
            )
            voces.append(voice_info)
        
        logger.info(f"Se encontraron {len(voces)} voces disponibles")
        
        return VoicesListResponse(
            voices=voces,
            total=len(voces)
        )
        
    except PermissionError as pe:
        logger.error(f"Error de permisos: {str(pe)}")
        raise HTTPException(
            status_code=403,
            detail=f"Error de permisos en ElevenLabs API: {str(pe)}"
        )
        
    except Exception as e:
        logger.error(f"Error obteniendo voces: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener las voces: {str(e)}"
        )


@router.get(
    "/cuentos/{cuento_id}/estado",
    summary="Verificar si existe audio para un cuento",
    description="Verifica si ya se generó audio para el cuento especificado"
)
async def verificar_audio_cuento(
    cuento_id: str = Path(..., description="ID del cuento")
) -> Dict[str, Any]:
    """
    Verifica si existe un archivo de audio para el cuento.
    
    Args:
        cuento_id: Identificador único del cuento
        
    Returns:
        Diccionario indicando si existe el audio y su URL si existe
    """
    try:
        existe = audio_service.audio_existe(cuento_id)
        
        if existe:
            audio_url = f"/data/audio/{cuento_id}.mp3"
            return {
                "existe": True,
                "audio_url": audio_url,
                "message": "El audio está disponible"
            }
        else:
            return {
                "existe": False,
                "audio_url": None,
                "message": "No se ha generado audio para este cuento"
            }
            
    except Exception as e:
        logger.error(f"Error verificando audio: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error al verificar el audio: {str(e)}"
        )


@router.get(
    "/configuracion",
    summary="Obtener configuración actual de audio",
    description="Devuelve la configuración actual del servicio de audio (voz, modelo, etc.)"
)
async def obtener_configuracion_audio() -> Dict[str, Any]:
    """
    Obtiene la configuración actual del servicio de audio.
    
    Returns:
        Diccionario con la configuración activa
    """
    from config import ELEVENLABS_MODEL_ID
    
    return {
        "voice_id": ELEVENLABS_VOICE_ID,
        "model_id": ELEVENLABS_MODEL_ID,
        "voice_name": "George",
        "voice_description": "Warm, Captivating Storyteller",
        "format": "mp3_44100_128",
        "language_support": "multilingual"
    }


@router.get(
    "/cuota",
    summary="Obtener información de cuota de ElevenLabs",
    description="Devuelve información sobre el uso de caracteres y límites de la cuenta"
)
async def obtener_cuota_usuario() -> Dict[str, Any]:
    """
    Obtiene información de la cuota del usuario en ElevenLabs.
    
    Returns:
        Diccionario con información de caracteres usados y disponibles
    """
    try:
        info = audio_service.obtener_info_usuario()
        
        if "error" in info:
            return {
                "available": False,
                "message": "No se pudo obtener información de cuota",
                "error": info["error"]
            }
        
        used = info.get("character_count", 0)
        limit = info.get("character_limit", 10000)
        remaining = limit - used
        
        return {
            "available": True,
            "character_count": used,
            "character_limit": limit,
            "characters_remaining": remaining,
            "percentage_used": round((used / limit) * 100, 2) if limit > 0 else 0,
            "warning": remaining < 1000
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo cuota: {str(e)}", exc_info=True)
        return {
            "available": False,
            "message": "No se pudo obtener información de cuota",
            "error": str(e)
        }
