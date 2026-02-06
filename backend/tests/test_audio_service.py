"""
Test rápido del servicio de audio
Ejecuta desde la raíz: python -m backend.test_audio_service
O desde backend: python test_audio_service.py
"""
import sys
from pathlib import Path

# Añadir el directorio padre al path para imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.services.audio_service import audio_service

def test_configuracion():
    """Verifica que el servicio esté correctamente configurado"""
    print("🔧 Verificando configuración del servicio de audio...")
    print(f"   ✓ Voice ID: {audio_service.voice_id}")
    print(f"   ✓ Model ID: {audio_service.model_id}")
    print(f"   ✓ Audio Directory: {audio_service.audio_dir}")
    print()

def test_voces_disponibles():
    """Obtiene las voces disponibles"""
    print("🎤 Obteniendo voces disponibles...")
    try:
        voces = audio_service.obtener_voces_disponibles()
        print(f"   ✓ Total de voces: {len(voces)}")
        print("\n   Primeras 5 voces:")
        for voz in voces[:5]:
            print(f"      - {voz['name']} (ID: {voz['voice_id']})")
        print()
        return True
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False

def test_generar_audio_prueba():
    """Genera un audio de prueba"""
    print("🎵 Generando audio de prueba...")
    texto_prueba = "Hola, soy CuentaCuentos. Este es un audio de prueba."
    
    try:
        ruta = audio_service.generar_audio_cuento(
            cuento_id=0,
            texto=texto_prueba
        )
        print(f"   ✓ Audio generado en: {ruta}")
        
        # Verificar que existe
        if audio_service.audio_existe(0):
            print(f"   ✓ Archivo verificado")
            
            # Limpieza
            audio_service.eliminar_audio(0)
            print(f"   ✓ Archivo de prueba eliminado")
        
        print()
        return True
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False

if __name__ == "__main__":
    print("\n" + "="*60)
    print("  TEST DEL SERVICIO DE AUDIO - ELEVENLABS")
    print("="*60 + "\n")
    
    test_configuracion()
    
    if test_voces_disponibles():
        test_generar_audio_prueba()
    
    print("="*60)
    print("  Test completado")
    print("="*60 + "\n")
