"""
Script para verificar voces disponibles y permisos de API
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.services.audio_service import audio_service
from elevenlabs.client import ElevenLabs
from backend.config import ELEVENLABS_API_KEY

def verificar_voces_disponibles():
    """Verifica qué voces están disponibles para usar"""
    print("\n" + "="*70)
    print("  VERIFICACIÓN DE VOCES DISPONIBLES - ELEVENLABS")
    print("="*70 + "\n")
    
    client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
    
    # Intentar obtener información del usuario
    print("📊 Información de tu cuenta:")
    try:
        user = client.user.get()
        print(f"   ✓ Usuario ID: {user.user_id if hasattr(user, 'user_id') else 'N/A'}")
        
        if hasattr(user, 'subscription'):
            sub = user.subscription
            print(f"   ✓ Plan: {sub.tier if hasattr(sub, 'tier') else 'N/A'}")
            print(f"   ✓ Caracteres disponibles: {sub.character_count if hasattr(sub, 'character_count') else 'N/A'}")
            print(f"   ✓ Límite de caracteres: {sub.character_limit if hasattr(sub, 'character_limit') else 'N/A'}")
    except Exception as e:
        print(f"   ⚠ No se pudo obtener info de la cuenta: {str(e)[:100]}")
    
    print("\n" + "-"*70 + "\n")
    
    # Intentar listar TODAS las voces (incluyendo las tuyas)
    print("🎤 Intentando obtener TODAS las voces de tu cuenta...\n")
    
    try:
        # Método 1: voices.get_all() si existe
        try:
            all_voices = client.voices.get_all()
            voces = all_voices.voices if hasattr(all_voices, 'voices') else []
        except:
            # Método 2: voices.search()
            try:
                response = client.voices.search()
                voces = response.voices if hasattr(response, 'voices') else []
            except Exception as e2:
                print(f"   ⚠ Error obteniendo voces: {str(e2)[:100]}\n")
                voces = []
        
        if voces:
            print(f"📋 Total de voces encontradas: {len(voces)}\n")
            
            voces_propias = []
            voces_compartidas = []
            voces_biblioteca = []
            
            for voz in voces:
                categoria = "Desconocida"
                
                # Clasificar voces
                if hasattr(voz, 'category'):
                    if voz.category == 'generated':
                        voces_propias.append(voz)
                        categoria = "Clonada/Generada (TUYA)"
                    elif voz.category == 'professional':
                        voces_biblioteca.append(voz)
                        categoria = "Biblioteca Pro (Requiere pago)"
                    elif voz.category == 'premade':
                        voces_biblioteca.append(voz)
                        categoria = "Pre-hechas (Verificar acceso)"
                    else:
                        categoria = f"Categoría: {voz.category}"
                
                # Si no tiene categoría, intentar inferir
                elif hasattr(voz, 'sharing'):
                    if voz.sharing and hasattr(voz.sharing, 'status'):
                        if voz.sharing.status == 'enabled':
                            voces_compartidas.append(voz)
                            categoria = "Compartida"
                else:
                    voces_biblioteca.append(voz)
                
                print(f"   • {voz.name}")
                print(f"     ID: {voz.voice_id}")
                print(f"     Tipo: {categoria}")
                
                if hasattr(voz, 'labels') and voz.labels:
                    labels_str = ", ".join([f"{k}: {v}" for k, v in voz.labels.items()])
                    print(f"     Etiquetas: {labels_str}")
                
                print()
            
            # Resumen
            print("\n" + "-"*70)
            print("📊 RESUMEN:")
            print("-"*70)
            print(f"   🟢 Voces propias (clonadas/generadas): {len(voces_propias)}")
            print(f"   🔵 Voces compartidas: {len(voces_compartidas)}")
            print(f"   🔴 Voces de biblioteca: {len(voces_biblioteca)}")
            
            if voces_propias:
                print("\n   ✅ VOCES QUE PUEDES USAR (Propias):")
                for voz in voces_propias:
                    print(f"      • {voz.name} - ID: {voz.voice_id}")
            
            if voces_compartidas:
                print("\n   ⚠️  VOCES COMPARTIDAS (Verificar):")
                for voz in voces_compartidas:
                    print(f"      • {voz.name} - ID: {voz.voice_id}")
            
        else:
            print("   ❌ No se encontraron voces")
            
    except Exception as e:
        print(f"   ❌ Error general: {str(e)}")
    
    print("\n" + "="*70)
    
    # Test de generación con voz actual
    print("\n🧪 TEST: Generando audio de prueba con tu voz configurada...")
    print(f"   Usando voz ID: {audio_service.voice_id}\n")
    
    try:
        texto_corto = "Hola, este es un test."
        ruta = audio_service.generar_audio_cuento(
            cuento_id=999,
            texto=texto_corto
        )
        print(f"   ✅ ¡Audio generado exitosamente!")
        print(f"   📁 Guardado en: {ruta}")
        
        # Limpiar
        audio_service.eliminar_audio(999)
        print(f"   🗑️  Archivo de prueba eliminado")
        
    except Exception as e:
        error_msg = str(e)
        print(f"   ❌ Error: {error_msg[:200]}")
        
        if "payment_required" in error_msg:
            print("\n   💡 SOLUCIÓN: Esta voz requiere plan de pago.")
            print("      - Opción 1: Clona tu propia voz (GRATIS)")
            print("      - Opción 2: Actualiza a un plan de pago")
        elif "quota_exceeded" in error_msg:
            print("\n   💡 Has excedido tu cuota mensual gratuita")
    
    print("\n" + "="*70 + "\n")

if __name__ == "__main__":
    verificar_voces_disponibles()
