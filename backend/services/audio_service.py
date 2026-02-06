"""
Servicio para generar audio de cuentos usando ElevenLabs TTS
"""
import os
from pathlib import Path
from typing import Optional
from elevenlabs.client import ElevenLabs
from config import (
    ELEVENLABS_API_KEY,
    ELEVENLABS_VOICE_ID,
    ELEVENLABS_MODEL_ID,
    DATA_DIR
)


class AudioService:
    """Servicio para gestionar la generación de audio de cuentos"""
    
    def __init__(self):
        """Inicializar cliente de ElevenLabs"""
        if not ELEVENLABS_API_KEY:
            raise ValueError(
                "ELEVENLABS_API_KEY no está configurada. "
                "Por favor, añade tu API key al archivo .env"
            )
        
        self.client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
        self.voice_id = ELEVENLABS_VOICE_ID
        self.model_id = ELEVENLABS_MODEL_ID
        
        # Crear directorio para audios si no existe
        self.audio_dir = DATA_DIR / "audio"
        self.audio_dir.mkdir(parents=True, exist_ok=True)
    
    def generar_audio_cuento(
        self, 
        cuento_id: int, 
        texto: str,
        voice_id: Optional[str] = None,
        output_format: str = "mp3_44100_128"
    ) -> str:
        """
        Genera audio para un cuento usando ElevenLabs TTS
        
        Args:
            cuento_id: ID del cuento
            texto: Texto del cuento a convertir a audio
            voice_id: ID de la voz (opcional, usa la configurada por defecto)
            output_format: Formato de salida del audio
            
        Returns:
            str: Path relativo del archivo de audio generado
            
        Raises:
            Exception: Si hay error en la generación del audio
        """
        try:
            # Usar voz personalizada o la por defecto
            voz = voice_id or self.voice_id
            
            # Generar audio con ElevenLabs
            audio_generator = self.client.text_to_speech.convert(
                text=texto,
                voice_id=voz,
                model_id=self.model_id,
                output_format=output_format
            )
            
            # Nombre del archivo
            filename = f"cuento_{cuento_id}.mp3"
            filepath = self.audio_dir / filename
            
            # Guardar audio en disco
            with open(filepath, "wb") as f:
                for chunk in audio_generator:
                    if chunk:
                        f.write(chunk)
            
            # Retornar path relativo para acceso HTTP
            return f"data/audio/{filename}"
            
        except Exception as e:
            error_msg = str(e)
            
            # Detectar error de cuota excedida
            if "quota_exceeded" in error_msg or "quota" in error_msg.lower():
                # Extraer información útil del error
                if "have" in error_msg and "credits remaining" in error_msg:
                    raise Exception(
                        f"⚠️ Cuota de ElevenLabs excedida. "
                        f"El texto requiere más caracteres de los que tienes disponibles en tu plan gratuito. "
                        f"Intenta con un texto más corto o actualiza tu plan."
                    )
                else:
                    raise Exception("⚠️ Has excedido tu cuota mensual de ElevenLabs. Intenta con textos más cortos o actualiza tu plan.")
            
            # Otros errores
            raise Exception(f"Error generando audio: {str(e)}")
    
    def obtener_voces_disponibles(self) -> list:
        """
        Obtiene lista de voces disponibles en ElevenLabs
        
        Returns:
            list: Lista de diccionarios con información de voces
            
        Raises:
            Exception: Si hay error obteniendo las voces
        """
        try:
            response = self.client.voices.search()
            return [
                {
                    "voice_id": voice.voice_id,
                    "name": voice.name,
                    "labels": voice.labels if hasattr(voice, 'labels') else {},
                    "preview_url": voice.preview_url if hasattr(voice, 'preview_url') else None
                }
                for voice in response.voices
            ]
        except Exception as e:
            # Si no tiene permisos, retornar lista con la voz configurada
            error_msg = str(e)
            if "missing_permissions" in error_msg or "voices_read" in error_msg:
                return [
                    {
                        "voice_id": self.voice_id,
                        "name": "Voz Configurada",
                        "labels": {"note": "API key con permisos limitados"},
                        "preview_url": None
                    }
                ]
            raise Exception(f"Error obteniendo voces: {str(e)}")
    
    def eliminar_audio(self, cuento_id: int) -> bool:
        """
        Elimina el archivo de audio de un cuento
        
        Args:
            cuento_id: ID del cuento
            
        Returns:
            bool: True si se eliminó correctamente, False si no existía
            
        Raises:
            Exception: Si hay error eliminando el archivo
        """
        try:
            filename = f"cuento_{cuento_id}.mp3"
            filepath = self.audio_dir / filename
            
            if filepath.exists():
                filepath.unlink()
                return True
            return False
            
        except Exception as e:
            raise Exception(f"Error eliminando audio: {str(e)}")
    
    def audio_existe(self, cuento_id: int) -> bool:
        """
        Verifica si ya existe un audio generado para un cuento
        
        Args:
            cuento_id: ID del cuento
            
        Returns:
            bool: True si existe el archivo de audio
        """
        filename = f"cuento_{cuento_id}.mp3"
        filepath = self.audio_dir / filename
        return filepath.exists()
    
    def obtener_ruta_audio(self, cuento_id: int) -> Optional[str]:
        """
        Obtiene la ruta del audio si existe
        
        Args:
            cuento_id: ID del cuento
            
        Returns:
            str: Path relativo si existe, None si no existe
        """
        if self.audio_existe(cuento_id):
            return f"data/audio/cuento_{cuento_id}.mp3"
        return None
    
    def obtener_info_usuario(self) -> dict:
        """
        Obtiene información de la cuenta del usuario (cuota, etc.)
        
        Returns:
            dict: Información de la cuenta si está disponible
        """
        try:
            user_info = self.client.user.get()
            return {
                "character_count": getattr(user_info, 'character_count', 0),
                "character_limit": getattr(user_info, 'character_limit', 10000),
                "can_use_delayed_payment_methods": getattr(user_info, 'can_use_delayed_payment_methods', False)
            }
        except Exception as e:
            # Si no se puede obtener info, retornar valores por defecto
            return {
                "character_count": 0,
                "character_limit": 10000,
                "error": str(e)
            }


# Instancia global del servicio
audio_service = AudioService()
