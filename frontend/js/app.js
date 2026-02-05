const API_BASE_URL = 'http://127.0.0.1:8000';

let currentCharacters = [];

async function loadCharacters() {
    console.log('[loadCharacters] Iniciando carga de personajes...');
    try {
        const response = await fetch(`${API_BASE_URL}/characters`);
        console.log('[loadCharacters] Response status:', response.status);
        
        currentCharacters = await response.json();
        console.log('[loadCharacters] Personajes recibidos:', currentCharacters);
        
        const checkboxContainer = document.getElementById('characters_checkboxes');
        checkboxContainer.innerHTML = '';
        
        if (currentCharacters.length === 0) {
            checkboxContainer.innerHTML = '<p style="color: #666;">No hay personajes disponibles</p>';
            return;
        }
        
        currentCharacters.forEach(character => {
            const checkboxItem = document.createElement('div');
            checkboxItem.className = 'checkbox-item';
            
            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.id = `char_${character.id}`;
            checkbox.name = 'characters';
            checkbox.value = character.nombre;
            
            const label = document.createElement('label');
            label.htmlFor = `char_${character.id}`;
            label.textContent = `${character.nombre} - ${character.edad_aparente || 'Personaje'}`;
            
            checkboxItem.appendChild(checkbox);
            checkboxItem.appendChild(label);
            checkboxContainer.appendChild(checkboxItem);
        });
        console.log('[loadCharacters] ✅ Personajes cargados exitosamente');
    } catch (error) {
        console.error('[loadCharacters] ❌ Error:', error);
        document.getElementById('characters_checkboxes').innerHTML = 
            '<p style="color: red;">Error al cargar personajes</p>';
    }
}

function showLoading() {
    document.querySelector('.loading').classList.add('visible');
    document.querySelector('button').disabled = true;
    document.getElementById('result').classList.remove('visible');
}

function hideLoading() {
    document.querySelector('.loading').classList.remove('visible');
    document.querySelector('button').disabled = false;
}

function showError(message) {
    const resultDiv = document.getElementById('result');
    resultDiv.innerHTML = `
        <div class="error">
            <strong>Error:</strong> ${message}
        </div>
    `;
    resultDiv.classList.add('visible');
}

function displayResults(story, critique) {
    const resultDiv = document.getElementById('result');
    
    let html = `
        <div class="result-content">
            <h3 class="story-title">${story.title}</h3>
            <div class="story-text">${story.content}</div>
        </div>
    `;
    
    if (critique && critique.analysis) {
        html += `
            <div class="critique-content">
                <h4 class="critique-title">Análisis y Sugerencias de Mejora</h4>
                <div class="critique-text">${critique.analysis}</div>
            </div>
        `;
    }
    
    resultDiv.innerHTML = html;
    resultDiv.classList.add('visible');
    
    // Scroll al resultado
    resultDiv.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

async function generateStory(event) {
    console.log('[generateStory] 🚀 Iniciando generación de cuento...');
    event.preventDefault();
    
    const formData = new FormData(event.target);
    
    // Obtener personajes seleccionados (checkboxes)
    const selectedCharacters = Array.from(document.querySelectorAll('input[name="characters"]:checked'))
        .map(cb => cb.value);
    console.log('[generateStory] Personajes seleccionados:', selectedCharacters);
    
    const storyData = {
        theme: formData.get('theme'),
        character_names: selectedCharacters.length > 0 ? selectedCharacters : null,
        moral_lesson: formData.get('moral_lesson') || null,
        target_age: formData.get('target_age') ? parseInt(formData.get('target_age')) : 6,
        length: formData.get('length'),
        special_elements: formData.get('special_elements') || null
    };

    console.log('[generateStory] Datos del cuento:', storyData);

    // Validación simple: solo tema es obligatorio
    if (!storyData.theme || storyData.theme.trim() === '') {
        console.warn('[generateStory] ⚠️ Validación fallida: tema vacío');
        showError('Por favor, escribe un tema para el cuento.');
        return;
    }

    showLoading();

    try {
        console.log('[generateStory] 📡 Enviando request a:', `${API_BASE_URL}/stories/generate`);
        console.log('[generateStory] 📦 Payload:', JSON.stringify(storyData, null, 2));
        
        const response = await fetch(`${API_BASE_URL}/stories/generate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(storyData)
        });

        console.log('[generateStory] Response status:', response.status);
        console.log('[generateStory] Response headers:', Object.fromEntries(response.headers.entries()));

        if (!response.ok) {
            let errorMessage = 'Error generating story';
            try {
                const errorData = await response.json();
                console.error('[generateStory] ❌ Error response:', errorData);
                errorMessage = errorData.detail || errorMessage;
            } catch (jsonError) {
                console.error('[generateStory] ❌ Error parseando JSON de error:', jsonError);
                const errorText = await response.text();
                console.error('[generateStory] ❌ Respuesta en texto:', errorText);
                errorMessage = `Error ${response.status}: ${errorText}`;
            }
            throw new Error(errorMessage);
        }

        const result = await response.json();
        console.log('[generateStory] ✅ Cuento recibido:', result);
        
        // El backend devuelve el cuento directamente, no en un wrapper
        displayResults(result, null);
        
        console.log('[generateStory] ✅ Proceso completado exitosamente');
        
    } catch (error) {
        console.error('[generateStory] ❌ Error completo:', error);
        console.error('[generateStory] Stack trace:', error.stack);
        showError(error.message || 'Error al generar el cuento. Por favor, inténtalo de nuevo.');
    } finally {
        hideLoading();
    }
}

// Event Listeners
document.addEventListener('DOMContentLoaded', function() {
    console.log('🎬 [DOMContentLoaded] Aplicación iniciada');
    console.log('[DOMContentLoaded] API Base URL:', API_BASE_URL);
    
    loadCharacters();
    
    const form = document.getElementById('storyForm');
    form.addEventListener('submit', generateStory);
    
    console.log('[DOMContentLoaded] ✅ Event listeners configurados');
});