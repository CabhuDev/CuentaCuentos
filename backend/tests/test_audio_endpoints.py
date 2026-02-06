"""
Script de prueba para los endpoints de audio.
Verifica que todos los endpoints del router audio.py funcionen correctamente.
"""
import sys
import os

# Agregar el directorio backend al path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

import asyncio
from fastapi.testclient import TestClient
from main import app

# Crear cliente de prueba
client = TestClient(app)


def test_obtener_configuracion():
    """Prueba el endpoint de configuración"""
    print("\n🔧 Probando GET /audio/configuracion")
    response = client.get("/audio/configuracion")
    
    assert response.status_code == 200, f"Error: {response.status_code}"
    data = response.json()
    
    print(f"   ✓ Voice ID: {data.get('voice_id')}")
    print(f"   ✓ Model ID: {data.get('model_id')}")
    print(f"   ✓ Voice Name: {data.get('voice_name')}")
    print(f"   ✓ Description: {data.get('voice_description')}")
    
    return data


def test_obtener_voces():
    """Prueba el endpoint de lista de voces"""
    print("\n🎤 Probando GET /audio/voces")
    response = client.get("/audio/voces")
    
    assert response.status_code == 200, f"Error: {response.status_code}"
    data = response.json()
    
    print(f"   ✓ Total de voces: {data.get('total')}")
    print(f"   ✓ Voces disponibles: {len(data.get('voices', []))}")
    
    # Mostrar primeras 3 voces
    for i, voz in enumerate(data.get('voices', [])[:3]):
        print(f"      - {voz['name']} ({voz['voice_id']})")
    
    return data


def test_verificar_audio_no_existe():
    """Prueba verificación de audio que no existe"""
    print("\n🔍 Probando GET /audio/cuentos/test_999/estado (no existe)")
    response = client.get("/audio/cuentos/test_999/estado")
    
    assert response.status_code == 200, f"Error: {response.status_code}"
    data = response.json()
    
    print(f"   ✓ Existe: {data.get('existe')}")
    print(f"   ✓ Message: {data.get('message')}")
    
    assert data.get('existe') == False, "Debería no existir"
    
    return data


def test_generar_audio():
    """Prueba generación de audio"""
    print("\n🎵 Probando POST /audio/cuentos/test_001/generar")
    
    payload = {
        "texto": "Había una vez, en un bosque mágico, un pequeño conejo llamado Martín que soñaba con volar como los pájaros.",
        "cuento_id": "test_001"
    }
    
    response = client.post("/audio/cuentos/test_001/generar", json=payload)
    
    assert response.status_code == 200, f"Error: {response.status_code} - {response.text}"
    data = response.json()
    
    print(f"   ✓ Success: {data.get('success')}")
    print(f"   ✓ Audio URL: {data.get('audio_url')}")
    print(f"   ✓ File Path: {data.get('file_path')}")
    print(f"   ✓ Duration: {data.get('duration')}s")
    print(f"   ✓ Characters: {data.get('characters_used')}")
    print(f"   ✓ Message: {data.get('message')}")
    
    assert data.get('success') == True, "La generación debería ser exitosa"
    
    return data


def test_verificar_audio_existe():
    """Prueba verificación de audio que existe"""
    print("\n✅ Probando GET /audio/cuentos/test_001/estado (existe)")
    response = client.get("/audio/cuentos/test_001/estado")
    
    assert response.status_code == 200, f"Error: {response.status_code}"
    data = response.json()
    
    print(f"   ✓ Existe: {data.get('existe')}")
    print(f"   ✓ Audio URL: {data.get('audio_url')}")
    print(f"   ✓ Message: {data.get('message')}")
    
    assert data.get('existe') == True, "El audio debería existir"
    
    return data


def test_eliminar_audio():
    """Prueba eliminación de audio"""
    print("\n🗑️ Probando DELETE /audio/cuentos/test_001")
    response = client.delete("/audio/cuentos/test_001")
    
    assert response.status_code == 200, f"Error: {response.status_code}"
    data = response.json()
    
    print(f"   ✓ Success: {data.get('success')}")
    print(f"   ✓ Message: {data.get('message')}")
    
    assert data.get('success') == True, "La eliminación debería ser exitosa"
    
    return data


def test_eliminar_audio_no_existe():
    """Prueba eliminación de audio que no existe"""
    print("\n❌ Probando DELETE /audio/cuentos/test_999 (no existe)")
    response = client.delete("/audio/cuentos/test_999")
    
    # Debería retornar 404
    assert response.status_code == 404, f"Debería ser 404, fue: {response.status_code}"
    data = response.json()
    
    print(f"   ✓ Status: {response.status_code}")
    print(f"   ✓ Detail: {data.get('detail')}")
    
    return data


def test_generar_audio_sin_texto():
    """Prueba generación sin texto (validación)"""
    print("\n⚠️ Probando POST /audio/cuentos/test_002/generar (sin texto)")
    
    payload = {"texto": "muy corto"}  # Menos de 10 caracteres
    
    response = client.post("/audio/cuentos/test_002/generar", json=payload)
    
    # Debería retornar 400
    assert response.status_code == 400, f"Debería ser 400, fue: {response.status_code}"
    data = response.json()
    
    print(f"   ✓ Status: {response.status_code}")
    print(f"   ✓ Detail: {data.get('detail')}")
    
    return data


def run_all_tests():
    """Ejecuta todas las pruebas"""
    print("=" * 60)
    print("🧪 PRUEBAS DE ENDPOINTS DE AUDIO")
    print("=" * 60)
    
    try:
        # Pruebas de lectura (sin efectos secundarios)
        test_obtener_configuracion()
        test_obtener_voces()
        test_verificar_audio_no_existe()
        
        # Pruebas con efectos (crear/eliminar)
        test_generar_audio()
        test_verificar_audio_existe()
        test_eliminar_audio()
        
        # Pruebas de validación
        test_eliminar_audio_no_existe()
        test_generar_audio_sin_texto()
        
        print("\n" + "=" * 60)
        print("✅ TODAS LAS PRUEBAS PASARON EXITOSAMENTE")
        print("=" * 60)
        
    except AssertionError as e:
        print("\n" + "=" * 60)
        print(f"❌ PRUEBA FALLÓ: {e}")
        print("=" * 60)
        raise
    
    except Exception as e:
        print("\n" + "=" * 60)
        print(f"💥 ERROR INESPERADO: {e}")
        print("=" * 60)
        raise


if __name__ == "__main__":
    run_all_tests()
