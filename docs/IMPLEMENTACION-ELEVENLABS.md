# Implementación de ElevenLabs Text-to-Speech en CuentaCuentos

## 📋 Objetivo
Añadir funcionalidad de generación de audio para los cuentos generados, permitiendo a los usuarios escuchar los cuentos con voces naturales y expresivas.

---

## 🚀 Flujo de Implementación

### **Fase 1: Configuración Inicial**

#### 1.1. Obtener API Key de ElevenLabs

1. Visita [https://elevenlabs.io](https://elevenlabs.io)
2. Crea una cuenta o inicia sesión
3. Ve a **Profile Settings** → **API Keys**
4. Copia tu API key (formato: `sk_...`)

#### 1.2. Configurar Variables de Entorno

Editar `backend/config.py`:

```python
# Añadir al archivo config.py
ELEVENLABS_API_KEY: str = os.getenv("ELEVENLABS_API_KEY", "")
ELEVENLABS_VOICE_ID: str = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")  # Voz por defecto
ELEVENLABS_MODEL_ID: str = os.getenv("ELEVENLABS_MODEL_ID", "eleven_multilingual_v2")
```

Crear/editar archivo `.env` en la raíz del proyecto:

```env
# ElevenLabs Configuration
ELEVENLABS_API_KEY=tu_api_key_aqui
ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM
ELEVENLABS_MODEL_ID=eleven_multilingual_v2
```

#### 1.3. Instalar Dependencia

```bash
pip install elevenlabs
```

Actualizar `backend/requirements.txt`:
```txt
elevenlabs
```

---

### **Fase 2: Backend - Implementación del Servicio**

#### 2.1. Crear Servicio de Audio (`backend/services/audio_service.py`)

```python
"""
Servicio para generar audio de cuentos usando ElevenLabs TTS
"""
import os
from pathlib import Path
from typing import Optional
from elevenlabs.client import ElevenLabs
from backend.config import (
    ELEVENLABS_API_KEY,
    ELEVENLABS_VOICE_ID,
    ELEVENLABS_MODEL_ID
)

class AudioService:
    def __init__(self):
        """Inicializar cliente de ElevenLabs"""
        if not ELEVENLABS_API_KEY:
            raise ValueError("ELEVENLABS_API_KEY no está configurada")
        
        self.client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
        self.voice_id = ELEVENLABS_VOICE_ID
        self.model_id = ELEVENLABS_MODEL_ID
        
        # Crear directorio para audios si no existe
        self.audio_dir = Path("backend/data/audio")
        self.audio_dir.mkdir(parents=True, exist_ok=True)
    
    def generar_audio_cuento(
        self, 
        cuento_id: int, 
        texto: str,
        voice_id: Optional[str] = None,
        output_format: str = "mp3_44100_128"
    ) -> str:
        """
        Genera audio para un cuento
        
        Args:
            cuento_id: ID del cuento
            texto: Texto del cuento a convertir
            voice_id: ID de la voz (opcional, usa la por defecto)
            output_format: Formato de salida del audio
            
        Returns:
            str: Path relativo del archivo de audio generado
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
            
            # Retornar path relativo
            return f"data/audio/{filename}"
            
        except Exception as e:
            raise Exception(f"Error generando audio: {str(e)}")
    
    def obtener_voces_disponibles(self) -> list:
        """
        Obtiene lista de voces disponibles en ElevenLabs
        
        Returns:
            list: Lista de voces disponibles
        """
        try:
            response = self.client.voices.search()
            return [
                {
                    "voice_id": voice.voice_id,
                    "name": voice.name,
                    "labels": voice.labels if hasattr(voice, 'labels') else {}
                }
                for voice in response.voices
            ]
        except Exception as e:
            raise Exception(f"Error obteniendo voces: {str(e)}")
    
    def eliminar_audio(self, cuento_id: int) -> bool:
        """
        Elimina el archivo de audio de un cuento
        
        Args:
            cuento_id: ID del cuento
            
        Returns:
            bool: True si se eliminó correctamente
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

# Instancia global del servicio
audio_service = AudioService()
```

---

### **Fase 3: Backend - Modelos y Schemas**

#### 3.1. Actualizar Schema de Cuento (`backend/models/schemas.py`)

```python
# Añadir al StoryResponse existente o crear nuevo schema

class AudioGenerationRequest(BaseModel):
    """Request para generar audio"""
    voice_id: Optional[str] = None
    
class AudioGenerationResponse(BaseModel):
    """Response de generación de audio"""
    success: bool
    audio_url: str
    message: Optional[str] = None

class VoiceInfo(BaseModel):
    """Información de una voz"""
    voice_id: str
    name: str
    labels: dict = {}
```

---

### **Fase 4: Backend - Router de Audio**

#### 4.1. Crear Router (`backend/routers/audio.py`)

```python
"""
Router para operaciones de audio
"""
from fastapi import APIRouter, HTTPException, status
from backend.services.audio_service import audio_service
from backend.models.schemas import (
    AudioGenerationRequest,
    AudioGenerationResponse,
    VoiceInfo
)
from backend.models.database_sqlite import obtener_cuento_por_id

router = APIRouter(prefix="/audio", tags=["audio"])

@router.post("/cuentos/{cuento_id}/generar", response_model=AudioGenerationResponse)
async def generar_audio_cuento(cuento_id: int, request: AudioGenerationRequest):
    """
    Genera audio para un cuento específico
    
    Args:
        cuento_id: ID del cuento
        request: Configuración de generación (voz personalizada, etc.)
        
    Returns:
        AudioGenerationResponse con URL del audio generado
    """
    try:
        # Obtener cuento de la base de datos
        cuento = obtener_cuento_por_id(cuento_id)
        
        if not cuento:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Cuento {cuento_id} no encontrado"
            )
        
        # Generar audio
        audio_path = audio_service.generar_audio_cuento(
            cuento_id=cuento_id,
            texto=cuento["contenido"],
            voice_id=request.voice_id
        )
        
        return AudioGenerationResponse(
            success=True,
            audio_url=f"/api/{audio_path}",
            message="Audio generado correctamente"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.delete("/cuentos/{cuento_id}")
async def eliminar_audio_cuento(cuento_id: int):
    """
    Elimina el audio de un cuento
    
    Args:
        cuento_id: ID del cuento
    """
    try:
        eliminado = audio_service.eliminar_audio(cuento_id)
        
        if not eliminado:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Audio no encontrado"
            )
        
        return {"success": True, "message": "Audio eliminado"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/voces", response_model=list[VoiceInfo])
async def obtener_voces_disponibles():
    """
    Obtiene lista de voces disponibles en ElevenLabs
    
    Returns:
        Lista de voces disponibles
    """
    try:
        voces = audio_service.obtener_voces_disponibles()
        return voces
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
```

#### 4.2. Registrar Router en `backend/main.py`

```python
# Añadir import
from backend.routers import audio

# Registrar router
app.include_router(audio.router, prefix="/api")
```

#### 4.3. Configurar servicio estático para audios en `backend/main.py`

```python
from fastapi.staticfiles import StaticFiles

# Añadir después de los otros routers
app.mount("/api/data/audio", StaticFiles(directory="backend/data/audio"), name="audio")
```

---

### **Fase 5: Frontend - Implementación UI**

#### 5.1. Actualizar `frontend/js/cuentos.js`

```javascript
// Añadir al final del archivo

/**
 * Genera audio para un cuento
 */
async function generarAudioCuento(cuentoId) {
    const btnAudio = document.getElementById(`btn-audio-${cuentoId}`);
    
    try {
        // Cambiar estado del botón
        btnAudio.disabled = true;
        btnAudio.innerHTML = '<span class="spinner"></span> Generando...';
        
        // Llamar al endpoint
        const response = await fetch(`/api/audio/cuentos/${cuentoId}/generar`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({})
        });
        
        if (!response.ok) {
            throw new Error('Error generando audio');
        }
        
        const data = await response.json();
        
        // Crear reproductor de audio
        mostrarReproductorAudio(cuentoId, data.audio_url);
        
        // Restaurar botón
        btnAudio.disabled = false;
        btnAudio.innerHTML = '🔊 Escuchar';
        
    } catch (error) {
        console.error('Error:', error);
        alert('Error al generar el audio. Por favor, intenta de nuevo.');
        
        // Restaurar botón
        btnAudio.disabled = false;
        btnAudio.innerHTML = '🎵 Generar Audio';
    }
}

/**
 * Muestra reproductor de audio
 */
function mostrarReproductorAudio(cuentoId, audioUrl) {
    const contenedor = document.getElementById(`audio-player-${cuentoId}`);
    
    contenedor.innerHTML = `
        <audio controls class="audio-player">
            <source src="${audioUrl}" type="audio/mpeg">
            Tu navegador no soporta el elemento de audio.
        </audio>
        <button onclick="eliminarAudio(${cuentoId})" class="btn-eliminar-audio">
            🗑️ Eliminar Audio
        </button>
    `;
    
    contenedor.style.display = 'block';
}

/**
 * Elimina el audio de un cuento
 */
async function eliminarAudio(cuentoId) {
    if (!confirm('¿Estás seguro de eliminar este audio?')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/audio/cuentos/${cuentoId}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) {
            throw new Error('Error eliminando audio');
        }
        
        // Ocultar reproductor
        const contenedor = document.getElementById(`audio-player-${cuentoId}`);
        contenedor.style.display = 'none';
        contenedor.innerHTML = '';
        
    } catch (error) {
        console.error('Error:', error);
        alert('Error al eliminar el audio.');
    }
}
```

#### 5.2. Actualizar HTML de las tarjetas de cuentos

En `frontend/cuentos.html` o donde generes las tarjetas, añadir:

```html
<div class="cuento-card" id="cuento-${cuento.id}">
    <h3>${cuento.titulo}</h3>
    <p>${cuento.contenido.substring(0, 150)}...</p>
    
    <!-- Botones existentes -->
    <div class="cuento-actions">
        <button onclick="verCuento(${cuento.id})">Ver Completo</button>
        <button onclick="editarCuento(${cuento.id})">Editar</button>
        
        <!-- NUEVO: Botón de audio -->
        <button 
            id="btn-audio-${cuento.id}" 
            onclick="generarAudioCuento(${cuento.id})"
            class="btn-audio">
            🎵 Generar Audio
        </button>
    </div>
    
    <!-- NUEVO: Contenedor para reproductor -->
    <div id="audio-player-${cuento.id}" class="audio-container" style="display: none;">
        <!-- El reproductor se insertará aquí dinámicamente -->
    </div>
</div>
```

#### 5.3. Añadir estilos en `frontend/css/styles.css`

```css
/* Estilos para botón de audio */
.btn-audio {
    background-color: #10b981;
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.3s ease;
}

.btn-audio:hover {
    background-color: #059669;
    transform: translateY(-2px);
}

.btn-audio:disabled {
    background-color: #9ca3af;
    cursor: not-allowed;
}

/* Contenedor de reproductor */
.audio-container {
    margin-top: 15px;
    padding: 15px;
    background-color: #f3f4f6;
    border-radius: 8px;
}

.audio-player {
    width: 100%;
    margin-bottom: 10px;
}

.btn-eliminar-audio {
    background-color: #ef4444;
    color: white;
    border: none;
    padding: 6px 12px;
    border-radius: 4px;
    cursor: pointer;
    font-size: 12px;
}

.btn-eliminar-audio:hover {
    background-color: #dc2626;
}

/* Spinner para carga */
.spinner {
    display: inline-block;
    width: 12px;
    height: 12px;
    border: 2px solid #ffffff;
    border-top-color: transparent;
    border-radius: 50%;
    animation: spin 0.6s linear infinite;
}

@keyframes spin {
    to { transform: rotate(360deg); }
}
```

---

### **Fase 6: Base de Datos (Opcional)**

Si quieres guardar la información del audio en la BD:

```sql
-- Añadir columna a la tabla de cuentos
ALTER TABLE cuentos ADD COLUMN audio_url TEXT;
ALTER TABLE cuentos ADD COLUMN audio_generado_at TIMESTAMP;
```

---

## 🧪 Testing

### Pruebas Manuales

1. **Generar audio de un cuento:**
   ```bash
   curl -X POST http://localhost:8000/api/audio/cuentos/1/generar \
     -H "Content-Type: application/json" \
     -d '{}'
   ```

2. **Obtener voces disponibles:**
   ```bash
   curl http://localhost:8000/api/audio/voces
   ```

3. **Eliminar audio:**
   ```bash
   curl -X DELETE http://localhost:8000/api/audio/cuentos/1
   ```

---

## 📊 Consideraciones

### Costos
- ElevenLabs tiene límites en el plan gratuito (~10,000 caracteres/mes)
- Monitorear uso en: https://elevenlabs.io/subscription

### Performance
- Generación puede tardar 10-30 segundos según longitud del cuento
- Considerar implementar cola de procesamiento para cuentos largos

### Almacenamiento
- Archivos MP3 ~200KB por minuto de audio
- Implementar limpieza periódica de audios antiguos

### Seguridad
- No exponer API key en frontend
- Validar que el cuento pertenece al usuario autenticado
- Limitar rate de generación de audios

---

## 🚀 Despliegue

1. Asegurar que `.env` está en `.gitignore`
2. Configurar variable de entorno en servidor de producción
3. Crear directorio `backend/data/audio` con permisos de escritura
4. Configurar CORS si frontend está en dominio diferente

---

## 📝 Checklist de Implementación

- [ ] Obtener API key de ElevenLabs
- [ ] Configurar variables de entorno
- [ ] Instalar dependencia `elevenlabs`
- [ ] Crear `audio_service.py`
- [ ] Actualizar schemas en `schemas.py`
- [ ] Crear router `audio.py`
- [ ] Registrar router en `main.py`
- [ ] Configurar servicio estático para audios
- [ ] Crear directorio `backend/data/audio`
- [ ] Actualizar JavaScript en `cuentos.js`
- [ ] Añadir botón en HTML
- [ ] Añadir estilos CSS
- [ ] Probar endpoint de generación
- [ ] Probar endpoint de eliminación
- [ ] Probar UI completa

---

## 🆘 Troubleshooting

### Error: "ELEVENLABS_API_KEY no está configurada"
- Verificar que el archivo `.env` existe
- Verificar que la variable está correctamente escrita
- Reiniciar el servidor backend

### Audio no se reproduce
- Verificar que el archivo se generó en `backend/data/audio`
- Verificar que el servicio estático está configurado
- Verificar CORS si el audio está en otro dominio

### Error 429 (Too Many Requests)
- Has excedido el límite de la API
- Esperar o actualizar plan en ElevenLabs

---

## 🔄 Mejoras Futuras

1. **Caché de audios:** Guardar audios generados para evitar regeneración
2. **Selector de voces:** Permitir elegir voz antes de generar
3. **Progress bar:** Mostrar progreso durante generación
4. **Queue system:** Procesar generaciones en background
5. **Fragmentación:** Dividir cuentos largos en fragmentos
6. **Descarga:** Permitir descargar el audio MP3

---

## 📚 Referencias

- [ElevenLabs API Docs](https://elevenlabs.io/docs/api-reference)
- [ElevenLabs Python SDK](https://github.com/elevenlabs/elevenlabs-python)
- [Modelos disponibles](https://elevenlabs.io/docs/models)
