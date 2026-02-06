const API_BASE_URL = 'http://127.0.0.1:8000';

// Cargar lista de cuentos guardados
async function loadStoriesList() {
    console.log('[loadStoriesList] 📚 Iniciando carga de cuentos guardados...');
    try {
        const response = await fetch(`${API_BASE_URL}/stories?limit=20`);
        console.log('[loadStoriesList] Response status:', response.status);
        
        if (!response.ok) {
            console.error('[loadStoriesList] ❌ Response no OK:', response.status);
            throw new Error('Error al cargar cuentos');
        }
        
        const stories = await response.json();
        console.log('[loadStoriesList] Cuentos recibidos:', stories.length, 'cuentos');
        console.log('[loadStoriesList] Datos:', stories);
        
        const storiesList = document.getElementById('stories-list');
        
        if (stories.length === 0) {
            storiesList.innerHTML = `
                <div class="empty-state">
                    <p>No hay cuentos guardados aún.</p>
                    <a href="index.html" class="btn-primary">Crear mi primer cuento ✨</a>
                </div>
            `;
            return;
        }
        
        storiesList.innerHTML = '';
        stories.forEach(story => {
            const card = document.createElement('div');
            card.className = 'story-card';
            card.onclick = () => showStoryDetails(story);
            
            const preview = story.content.substring(0, 150) + (story.content.length > 150 ? '...' : '');
            const date = new Date(story.created_at).toLocaleDateString('es-ES', {
                year: 'numeric',
                month: 'long',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });
            
            card.innerHTML = `
                <div class="story-card-title">${story.title}</div>
                <div class="story-card-meta">
                    <span>📅 ${date}</span>
                    <span>v${story.version}</span>
                </div>
                <div class="story-card-preview">${preview}</div>
                <div class="story-card-actions">
                    <button class="btn-audio-mini" data-story-id="${story.id}" title="Generar audio">
                        🎵 Audio
                    </button>
                    <button class="btn-play-mini hidden" data-story-id="${story.id}" title="Reproducir audio">
                        ▶️ Reproducir
                    </button>
                </div>
            `;
            
            // Agregar event listeners a los botones
            const audioBtn = card.querySelector('.btn-audio-mini');
            const playBtn = card.querySelector('.btn-play-mini');
            
            audioBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                generateAudio(story.id, story.content, audioBtn, playBtn);
            });
            
            playBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                playAudio(story.id);
            });
            
            storiesList.appendChild(card);
        });
        console.log('[loadStoriesList] ✅ Lista de cuentos renderizada exitosamente');
        
        // Verificar qué cuentos tienen audio generado
        updateAudioButtons();
        
    } catch (error) {
        console.error('[loadStoriesList] ❌ Error:', error);
        console.error('[loadStoriesList] Stack trace:', error.stack);
        document.getElementById('stories-list').innerHTML = 
            '<p class="loading-text" style="color: red;">Error al cargar los cuentos. Por favor, verifica que el servidor esté corriendo.</p>';
    }
}

// Mostrar detalles de un cuento
function showStoryDetails(story) {
    console.log('[showStoryDetails] 📖 Mostrando cuento:', story.title);
    console.log('[showStoryDetails] Datos completos:', story);
    
    // Ocultar lista, mostrar detalle
    document.getElementById('stories-list').classList.add('hidden');
    const detailDiv = document.getElementById('story-detail');
    detailDiv.classList.remove('hidden');
    
    const contentDiv = document.getElementById('story-content');
    
    // Verificar si tiene plantilla de ilustraciones
    const hasIllustrationTemplate = story.illustration_template && Object.keys(story.illustration_template).length > 0;
    console.log('[showStoryDetails] ¿Tiene plantilla de ilustraciones?', hasIllustrationTemplate);
    
    let illustrationButton = '';
    if (hasIllustrationTemplate) {
        illustrationButton = `
            <button class="btn-illustration-template" onclick="toggleIllustrationTemplate()">
                🎨 Ver Plantilla de Ilustraciones
            </button>
            <div id="illustration-template-container" class="illustration-template-container hidden">
                <h4>📐 Plantilla de Ilustraciones (JSON)</h4>
                <p class="template-description">Esta plantilla contiene prompts listos para generar ilustraciones con IA (Midjourney, DALL-E, Stable Diffusion, etc.)</p>
                <pre class="json-display">${JSON.stringify(story.illustration_template, null, 2)}</pre>
                <div class="template-actions">
                    <button class="btn-secondary" onclick="copyTemplateToClipboard()">
                        📋 Copiar JSON
                    </button>
                    <button class="btn-secondary" onclick="downloadTemplate()">
                        💾 Descargar JSON
                    </button>
                </div>
            </div>
        `;
    }
    
    contentDiv.innerHTML = `
        <div class="result-content">
            <h3 class="story-title">${story.title}</h3>
            <div class="story-meta">
                <span>📅 ${new Date(story.created_at).toLocaleDateString('es-ES', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit'
                })}</span>
                <span>Versión ${story.version}</span>
            </div>
            
            <!-- Controles de Audio -->
            <div class="audio-controls-container">
                <button id="btn-generate-audio" class="btn-audio-generate" onclick="generateAudioForCurrentStory()">
                    🎵 Generar Narración en Audio
                </button>
                <div id="audio-player-container" class="audio-player hidden">
                    <audio id="audio-player" controls>
                        <source id="audio-source" src="" type="audio/mpeg">
                        Tu navegador no soporta audio HTML5.
                    </audio>
                    <button class="btn-delete-audio" onclick="deleteAudioForCurrentStory()" title="Eliminar audio">
                        🗑️ Eliminar Audio
                    </button>
                </div>
                <div id="audio-status" class="audio-status"></div>
            </div>
            
            <div class="story-text">${story.content}</div>
            ${illustrationButton}
        </div>
    `;
    
    // Guardar referencia global al cuento actual para funciones de plantilla
    window.currentStory = story;
    
    // Verificar si ya existe audio para este cuento
    checkAudioExists(story.id).then(exists => {
        if (exists) {
            // Mostrar reproductor en lugar del botón de generar
            const button = document.getElementById('btn-generate-audio');
            const playerContainer = document.getElementById('audio-player-container');
            const audioSource = document.getElementById('audio-source');
            const audioPlayer = document.getElementById('audio-player');
            
            button.classList.add('hidden');
            audioSource.src = `${API_BASE_URL}/static/audio/${story.id}.mp3`;
            audioPlayer.load();
            playerContainer.classList.remove('hidden');
        }
    });
    
    // Scroll al top
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Toggle mostrar/ocultar plantilla de ilustraciones
function toggleIllustrationTemplate() {
    const container = document.getElementById('illustration-template-container');
    const button = document.querySelector('.btn-illustration-template');
    
    if (container.classList.contains('hidden')) {
        container.classList.remove('hidden');
        button.textContent = '🎨 Ocultar Plantilla de Ilustraciones';
        // Scroll suave al container
        setTimeout(() => {
            container.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }, 100);
    } else {
        container.classList.add('hidden');
        button.textContent = '🎨 Ver Plantilla de Ilustraciones';
    }
}

// Copiar plantilla al portapapeles
function copyTemplateToClipboard() {
    if (!window.currentStory || !window.currentStory.illustration_template) {
        alert('No hay plantilla disponible');
        return;
    }
    
    const json = JSON.stringify(window.currentStory.illustration_template, null, 2);
    navigator.clipboard.writeText(json).then(() => {
        const button = event.target;
        const originalText = button.textContent;
        button.textContent = '✅ Copiado!';
        button.style.background = '#28a745';
        
        setTimeout(() => {
            button.textContent = originalText;
            button.style.background = '';
        }, 2000);
    }).catch(err => {
        console.error('Error copiando:', err);
        alert('Error al copiar al portapapeles');
    });
}

// Descargar plantilla como archivo JSON
function downloadTemplate() {
    if (!window.currentStory || !window.currentStory.illustration_template) {
        alert('No hay plantilla disponible');
        return;
    }
    
    const json = JSON.stringify(window.currentStory.illustration_template, null, 2);
    const blob = new Blob([json], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    
    const a = document.createElement('a');
    a.href = url;
    a.download = `plantilla_ilustraciones_${window.currentStory.title.replace(/[^a-z0-9]/gi, '_')}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    console.log('[downloadTemplate] ✅ Plantilla descargada');
}

// Volver a la lista
function backToList() {
    console.log('[backToList] Volviendo a la lista');
    document.getElementById('story-detail').classList.add('hidden');
    document.getElementById('stories-list').classList.remove('hidden');
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Event Listeners
document.addEventListener('DOMContentLoaded', function() {
    console.log('🎬 [DOMContentLoaded] Página de cuentos iniciada');
    console.log('[DOMContentLoaded] API Base URL:', API_BASE_URL);
    
    loadStoriesList();
    
    const backButton = document.getElementById('back-button');
    if (backButton) {
        backButton.addEventListener('click', backToList);
    }
    
    console.log('[DOMContentLoaded] ✅ Event listeners configurados');
});

// ===== FUNCIONES DE AUDIO =====

// Verificar si existe audio para un cuento
async function checkAudioExists(storyId) {
    try {
        const response = await fetch(`${API_BASE_URL}/audio/cuentos/${storyId}/estado`);
        if (!response.ok) return false;
        const data = await response.json();
        return data.existe;
    } catch (error) {
        console.error('[checkAudioExists] Error:', error);
        return false;
    }
}

// Generar audio para el cuento actual (vista detalle)
async function generateAudioForCurrentStory() {
    if (!window.currentStory) {
        alert('No hay cuento seleccionado');
        return;
    }
    
    const storyId = window.currentStory.id;
    const texto = window.currentStory.content;
    
    const button = document.getElementById('btn-generate-audio');
    const statusDiv = document.getElementById('audio-status');
    
    // Deshabilitar botón y mostrar estado
    button.disabled = true;
    button.textContent = '⏳ Generando audio...';
    statusDiv.textContent = 'Generando narración con ElevenLabs...';
    statusDiv.className = 'audio-status info';
    
    try {
        const response = await fetch(`${API_BASE_URL}/audio/cuentos/${storyId}/generar`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ texto, cuento_id: storyId })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Error al generar audio');
        }
        
        const data = await response.json();
        console.log('[generateAudioForCurrentStory] Audio generado:', data);
        
        // Mostrar reproductor
        const playerContainer = document.getElementById('audio-player-container');
        const audioSource = document.getElementById('audio-source');
        const audioPlayer = document.getElementById('audio-player');
        
        audioSource.src = data.audio_url;
        audioPlayer.load();
        playerContainer.classList.remove('hidden');
        button.classList.add('hidden');
        
        statusDiv.textContent = `✅ Audio generado exitosamente (${data.characters_used} caracteres, ~${data.duration}s)`;
        statusDiv.className = 'audio-status success';
        
        // Ocultar mensaje después de 5 segundos
        setTimeout(() => {
            statusDiv.textContent = '';
            statusDiv.className = 'audio-status';
        }, 5000);
        
    } catch (error) {
        console.error('[generateAudioForCurrentStory] Error:', error);
        statusDiv.textContent = `❌ Error: ${error.message}`;
        statusDiv.className = 'audio-status error';
        button.disabled = false;
        button.textContent = '🎵 Generar Narración en Audio';
    }
}

// Eliminar audio del cuento actual
async function deleteAudioForCurrentStory() {
    if (!window.currentStory) return;
    
    if (!confirm('¿Estás seguro de eliminar el audio?')) return;
    
    const storyId = window.currentStory.id;
    const statusDiv = document.getElementById('audio-status');
    
    try {
        const response = await fetch(`${API_BASE_URL}/audio/cuentos/${storyId}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Error al eliminar audio');
        }
        
        // Ocultar reproductor y mostrar botón de generar
        const playerContainer = document.getElementById('audio-player-container');
        const button = document.getElementById('btn-generate-audio');
        
        playerContainer.classList.add('hidden');
        button.classList.remove('hidden');
        button.disabled = false;
        
        statusDiv.textContent = '🗑️ Audio eliminado correctamente';
        statusDiv.className = 'audio-status info';
        
        setTimeout(() => {
            statusDiv.textContent = '';
            statusDiv.className = 'audio-status';
        }, 3000);
        
    } catch (error) {
        console.error('[deleteAudioForCurrentStory] Error:', error);
        statusDiv.textContent = `❌ Error: ${error.message}`;
        statusDiv.className = 'audio-status error';
    }
}

// Generar audio desde tarjeta (lista de cuentos)
async function generateAudio(storyId, storyContent, buttonElement, playButton) {
    const originalText = buttonElement.textContent;
    buttonElement.disabled = true;
    buttonElement.textContent = '⏳';
    
    try {
        // Generar audio directamente con el contenido que ya tenemos
        const response = await fetch(`${API_BASE_URL}/audio/cuentos/${storyId}/generar`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ texto: storyContent, cuento_id: storyId })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Error al generar audio');
        }
        
        // Mostrar botón de reproducir
        buttonElement.classList.add('hidden');
        if (playButton) {
            playButton.classList.remove('hidden');
        }
        
        console.log('[generateAudio] ✅ Audio generado para:', storyId);
        
    } catch (error) {
        console.error('[generateAudio] Error:', error);
        alert(`Error al generar audio: ${error.message}`);
        buttonElement.disabled = false;
        buttonElement.textContent = originalText;
    }
}

// Reproducir audio desde tarjeta
function playAudio(storyId) {
    // Crear modal con reproductor
    const modal = document.createElement('div');
    modal.className = 'audio-modal';
    modal.innerHTML = `
        <div class="audio-modal-content">
            <h3>🎵 Reproducir Audio</h3>
            <audio controls autoplay style="width: 100%; margin: 20px 0;">
                <source src="${API_BASE_URL}/static/audio/${storyId}.mp3" type="audio/mpeg">
                Tu navegador no soporta audio HTML5.
            </audio>
            <button class="btn-secondary" onclick="this.closest('.audio-modal').remove()">
                Cerrar
            </button>
        </div>
    `;
    
    // Cerrar al hacer clic fuera
    modal.onclick = (e) => {
        if (e.target === modal) modal.remove();
    };
    
    document.body.appendChild(modal);
}

// Verificar audios existentes al cargar la lista
async function updateAudioButtons() {
    const audioButtons = document.querySelectorAll('.btn-audio-mini');
    
    for (const button of audioButtons) {
        const storyId = button.getAttribute('data-story-id');
        if (!storyId) continue;
        
        const exists = await checkAudioExists(storyId);
        
        if (exists) {
            button.classList.add('hidden');
            const playButton = button.nextElementSibling;
            if (playButton && playButton.classList.contains('btn-play-mini')) {
                playButton.classList.remove('hidden');
            }
        }
    }
}
