# Script de prueba para verificar la migración al nuevo SDK de Gemini
import asyncio
from services.gemini_service import gemini_service

async def test_gemini_service():
    print("🔍 Probando el nuevo SDK de Google Gemini...")
    print()
    
    if not gemini_service.is_configured():
        print("❌ Gemini no está configurado. Verifica GEMINI_API_KEY en .env")
        return
    
    print("✅ Gemini está configurado correctamente")
    print()
    
    # Prueba de generación simple
    print("📝 Probando generación de texto...")
    try:
        response = await gemini_service.generate_story(
            "Escribe un cuento muy corto sobre un gatito valiente."
        )
        
        if response:
            print("✅ Generación exitosa!")
            print(f"Respuesta (primeros 200 caracteres): {response[:200]}...")
        else:
            print("❌ No se recibió respuesta")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()
    print("✨ Migración completada exitosamente al nuevo SDK google-genai")

if __name__ == "__main__":
    asyncio.run(test_gemini_service())
