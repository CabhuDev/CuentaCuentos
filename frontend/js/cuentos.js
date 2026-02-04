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
            `;
            
            storiesList.appendChild(card);
        });
        console.log('[loadStoriesList] ✅ Lista de cuentos renderizada exitosamente');
        
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
            <div class="story-text">${story.content}</div>
            ${illustrationButton}
        </div>
    `;
    
    // Guardar referencia global al cuento actual para funciones de plantilla
    window.currentStory = story;
    
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
