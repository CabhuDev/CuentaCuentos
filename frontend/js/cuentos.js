// Usar ruta relativa para que funcione tanto en desarrollo como en producción
const API_BASE_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' 
    ? 'http://127.0.0.1:8000'
    : '/cuentacuentos/api';
const API_PREFIX = '/api';

// Cargar lista de cuentos guardados
async function loadStoriesList() {
    console.log('[loadStoriesList] 📚 Iniciando carga de cuentos guardados...');
    try {
        const response = await fetch(`${API_BASE_URL}${API_PREFIX}/stories?limit=20`);
        console.log('[loadStoriesList] Response status:', response.status);
        
        if (!response.ok) {
            console.error('[loadStoriesList] ❌ Response no OK:', response.status);
            throw new Error('Error al cargar cuentos');
        }
        
        const stories = await response.json();
        console.log('[loadStoriesList] Cuentos recibidos:', stories.length, 'cuentos');
        
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
        
        updateAudioButtons();
        
    } catch (error) {
        console.error('[loadStoriesList] ❌ Error:', error);
        document.getElementById('stories-list').innerHTML = 
            '<p class="loading-text" style="color: red;">Error al cargar los cuentos. Por favor, verifica que el servidor esté corriendo.</p>';
    }
}

// Mostrar detalles de un cuento
function showStoryDetails(story) {
    console.log('[showStoryDetails] 📖 Mostrando cuento:', story.title);
    
    document.getElementById('stories-list').classList.add('hidden');
    const detailDiv = document.getElementById('story-detail');
    detailDiv.classList.remove('hidden');
    
    const contentDiv = document.getElementById('story-content');
    
    const hasIllustrationTemplate = story.illustration_template && Object.keys(story.illustration_template).length > 0;
    
    let illustrationButton = '';
    if (hasIllustrationTemplate) {
        illustrationButton = `
            <button class="btn-illustration-template" onclick="toggleIllustrationTemplate()">
                🎨 Ver Plantilla de Ilustraciones
            </button>
            <div id="illustration-template-container" class="illustration-template-container hidden">
                <h4>📐 Plantilla de Ilustraciones (JSON)</h4>
                <p class="template-description">Esta plantilla contiene prompts listos para generar ilustraciones con IA (Midjourney, DALL-E, etc.)</p>
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
                <span>📅 ${new Date(story.created_at).toLocaleDateString('es-ES', { year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' })}</span>
                <span>Versión ${story.version}</span>
            </div>
            
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
    
    window.currentStory = story;
    
    checkAudioExists(story.id).then(status => {
        if (status.existe) {
            const button = document.getElementById('btn-generate-audio');
            const playerContainer = document.getElementById('audio-player-container');
            const audioSource = document.getElementById('audio-source');
            const audioPlayer = document.getElementById('audio-player');
            
            button.classList.add('hidden');
            audioSource.src = status.audio_url; // Usa la URL relativa del API
            audioPlayer.load();
            playerContainer.classList.remove('hidden');
        }
    });
    
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function toggleIllustrationTemplate() {
    const container = document.getElementById('illustration-template-container');
    const button = document.querySelector('.btn-illustration-template');
    
    if (container.classList.contains('hidden')) {
        container.classList.remove('hidden');
        button.textContent = '🎨 Ocultar Plantilla';
        setTimeout(() => container.scrollIntoView({ behavior: 'smooth', block: 'nearest' }), 100);
    } else {
        container.classList.add('hidden');
        button.textContent = '🎨 Ver Plantilla de Ilustraciones';
    }
}

function copyTemplateToClipboard() {
    if (!window.currentStory || !window.currentStory.illustration_template) return;
    
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
    });
}

function downloadTemplate() {
    if (!window.currentStory || !window.currentStory.illustration_template) return;
    
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
}

function backToList() {
    document.getElementById('story-detail').classList.add('hidden');
    document.getElementById('stories-list').classList.remove('hidden');
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

document.addEventListener('DOMContentLoaded', function() {
    loadStoriesList();
    const backButton = document.getElementById('back-button');
    if (backButton) backButton.addEventListener('click', backToList);
});

// ===== FUNCIONES DE AUDIO =====

async function checkAudioExists(storyId) {
    try {
        const response = await fetch(`${API_BASE_URL}${API_PREFIX}/audio/cuentos/${storyId}/estado`);
        if (!response.ok) return { existe: false };
        return await response.json();
    } catch (error) {
        console.error('[checkAudioExists] Error:', error);
        return { existe: false };
    }
}

async function generateAudioForCurrentStory() {
    if (!window.currentStory) return;
    
    const { id: storyId, content: texto } = window.currentStory;
    const button = document.getElementById('btn-generate-audio');
    const statusDiv = document.getElementById('audio-status');
    
    button.disabled = true;
    button.textContent = '⏳ Generando audio...';
    statusDiv.textContent = 'Generando narración con ElevenLabs...';
    statusDiv.className = 'audio-status info';
    
    try {
        const response = await fetch(`${API_BASE_URL}${API_PREFIX}/audio/cuentos/${storyId}/generar`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ texto, cuento_id: storyId })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Error al generar audio');
        }
        
        const data = await response.json();
        
        const playerContainer = document.getElementById('audio-player-container');
        const audioSource = document.getElementById('audio-source');
        const audioPlayer = document.getElementById('audio-player');
        
        audioSource.src = data.audio_url;
        audioPlayer.load();
        playerContainer.classList.remove('hidden');
        button.classList.add('hidden');
        
        statusDiv.textContent = `✅ Audio generado! (${data.characters_used} chars, ~${data.duration}s)`;
        statusDiv.className = 'audio-status success';
        
        setTimeout(() => { statusDiv.textContent = ''; statusDiv.className = 'audio-status'; }, 5000);
        
    } catch (error) {
        console.error('[generateAudioForCurrentStory] Error:', error);
        statusDiv.textContent = `❌ Error: ${error.message}`;
        statusDiv.className = 'audio-status error';
        button.disabled = false;
        button.textContent = '🎵 Generar Narración en Audio';
    }
}

async function deleteAudioForCurrentStory() {
    if (!window.currentStory) return;
    if (!confirm('¿Estás seguro de eliminar el audio?')) return;
    
    const { id: storyId } = window.currentStory;
    const statusDiv = document.getElementById('audio-status');
    
    try {
        const response = await fetch(`${API_BASE_URL}${API_PREFIX}/audio/cuentos/${storyId}`, { method: 'DELETE' });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Error al eliminar audio');
        }
        
        const playerContainer = document.getElementById('audio-player-container');
        const button = document.getElementById('btn-generate-audio');
        
        playerContainer.classList.add('hidden');
        button.classList.remove('hidden');
        button.disabled = false;
        
        statusDiv.textContent = '🗑️ Audio eliminado correctamente';
        statusDiv.className = 'audio-status info';
        
        setTimeout(() => { statusDiv.textContent = ''; statusDiv.className = 'audio-status'; }, 3000);
        
    } catch (error) {
        console.error('[deleteAudioForCurrentStory] Error:', error);
        statusDiv.textContent = `❌ Error: ${error.message}`;
        statusDiv.className = 'audio-status error';
    }
}

async function generateAudio(storyId, storyContent, buttonElement, playButton) {
    const originalText = buttonElement.textContent;
    buttonElement.disabled = true;
    buttonElement.textContent = '⏳';
    
    try {
        const response = await fetch(`${API_BASE_URL}${API_PREFIX}/audio/cuentos/${storyId}/generar`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ texto: storyContent, cuento_id: storyId })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Error al generar audio');
        }
        
        buttonElement.classList.add('hidden');
        if (playButton) playButton.classList.remove('hidden');
        
    } catch (error) {
        console.error('[generateAudio] Error:', error);
        alert(`Error al generar audio: ${error.message}`);
        buttonElement.disabled = false;
        buttonElement.textContent = originalText;
    }
}

async function playAudio(storyId) {
    const status = await checkAudioExists(storyId);
    if (!status.existe) {
        alert("El audio no está disponible. Intenta generarlo de nuevo.");
        return;
    }

    const modal = document.createElement('div');
    modal.className = 'audio-modal';
    modal.innerHTML = `
        <div class="audio-modal-content">
            <h3>🎵 Reproducir Audio</h3>
            <audio controls autoplay style="width: 100%; margin: 20px 0;">
                <source src="${status.audio_url}" type="audio/mpeg">
                Tu navegador no soporta audio HTML5.
            </audio>
            <button class="btn-secondary" onclick="this.closest('.audio-modal').remove()">
                Cerrar
            </button>
        </div>
    `;
    
    modal.onclick = (e) => { if (e.target === modal) modal.remove(); };
    document.body.appendChild(modal);
}

async function updateAudioButtons() {
    const audioButtons = document.querySelectorAll('.btn-audio-mini');
    
    for (const button of audioButtons) {
        const storyId = button.getAttribute('data-story-id');
        if (!storyId) continue;
        
        const status = await checkAudioExists(storyId);
        
        if (status.existe) {
            button.classList.add('hidden');
            const playButton = button.nextElementSibling;
            if (playButton && playButton.classList.contains('btn-play-mini')) {
                playButton.classList.remove('hidden');
            }
        }
    }
}
