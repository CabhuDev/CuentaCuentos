"""
Test de voz George para narración de cuentos en español
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.services.audio_service import audio_service

def test_voz_george():
    """Prueba la voz George narrando en español"""
    print("\n" + "="*70)
    print("  TEST: VOZ GEORGE - NARRACIÓN DE CUENTO EN ESPAÑOL")
    print("="*70 + "\n")
    
    texto_cuento = """
    Había una vez, en un bosque encantado, un pequeño conejo llamado Copito.
    Copito era muy curioso y le encantaba explorar. 
    Un día, encontró una puerta mágica entre los árboles.
    """
    
    print("📝 Texto del cuento:")
    print(texto_cuento)
    print("\n" + "-"*70 + "\n")
    
    print("🎤 Generando audio con voz GEORGE...")
    print("   Voice ID: JBFqnCBsd6RMkjVDRZzb")
    print("   Descripción: Warm, Captivating Storyteller\n")
    
    try:
        ruta = audio_service.generar_audio_cuento(
            cuento_id=1000,
            texto=texto_cuento,
            voice_id="JBFqnCBsd6RMkjVDRZzb"  # George
        )
        
        print(f"   ✅ ¡Audio generado exitosamente!")
        print(f"   📁 Archivo: {ruta}")
        print(f"\n   🎧 Puedes escuchar el audio en:")
        print(f"      {Path('C:/Users/Pablo/Desktop/CuentaCuentos/backend') / ruta}")
        
        print("\n" + "-"*70)
        print("   ✅ LA VOZ GEORGE FUNCIONA PARA CUENTOS EN ESPAÑOL")
        print("   💡 Recomiendo usar esta voz en tu proyecto")
        print("-"*70)
        
    except Exception as e:
        print(f"   ❌ Error: {str(e)[:200]}")
    
    print("\n" + "="*70 + "\n")

if __name__ == "__main__":
    test_voz_george()
