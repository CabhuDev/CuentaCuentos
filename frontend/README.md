# Frontend - CuentaCuentos AI

Interfaz web del sistema CuentaCuentos AI. Cliente ligero HTML/CSS/JavaScript que consume la API REST del backend.

## 🏗️ Arquitectura

```
frontend/
├── index.html              # 📝 Generador de cuentos (formulario)
├── cuentos.html            # 📚 Biblioteca de cuentos guardados
├── aprendizaje.html        # 🧠 Sistema de aprendizaje evolutivo (NUEVO)
├── css/
│   └── styles.css          # 🎨 Estilos compartidos
└── js/
    ├── app.js              # ⚙️ Lógica del generador
    └── cuentos.js          # 📖 Lógica de la biblioteca
```

## 📄 Páginas

### 1. **index.html** - Generador de Cuentos

Página principal para crear nuevos cuentos con IA.

**Características:**
- ✅ Formulario flexible (solo tema obligatorio)
- ✅ Selección múltiple de personajes (checkboxes)
- ✅ Campos opcionales: lección moral, edad, longitud, elementos especiales
- ✅ Muestra solo el cuento recién generado
- ✅ Navegación a biblioteca de cuentos

**URL:** `http://localhost:3000/index.html`

**Flujo de uso:**
1. Usuario escribe tema/escena (único campo obligatorio)
2. (Opcional) Selecciona personajes predefinidos
3. (Opcional) Completa otros campos
4. Click en "Generar Cuento ✨"
5. Ve el cuento generado inmediatamente

### 2. **cuentos.html** - Biblioteca de Cuentos

Página para explorar todos los cuentos guardados en la base de datos.

**Características:**
- ✅ Lista de cuentos con tarjetas clicables
- ✅ Vista previa (primeros 150 caracteres)
- ✅ Metadata: fecha de creación, versión
- ✅ Vista detalle completa al hacer clic
- ✅ **Plantilla de ilustraciones** - Botón para ver JSON con prompts de IA
- ✅ **Copiar/descargar template** - Listo para usar en DALL-E, Midjourney, etc.
- ✅ Navegación de regreso a la lista
- ✅ Estado vacío con link a crear primer cuento

**URL:** `http://localhost:3000/cuentos.html`

**Flujo de uso:**
1. Ve lista de todos los cuentos guardados
2. Click en una tarjeta para ver cuento completo
3. **Click en "🎨 Ver Plantilla de Ilustraciones"** para ver el JSON generado
4. Copiar al portapapeles o descargar como archivo .json
5. Botón "Volver a la lista" para regresar
6. Link "Crear Nuevo Cuento" para ir al generador

### 3. **aprendizaje.html** - Sistema de Aprendizaje Evolutivo (NUEVO)

Página para visualizar cómo el sistema aprende y mejora con cada cuento generado.

**Características:**
- ✅ **Estadísticas en tiempo real:**
  - Total de síntesis realizadas
  - Lecciones aprendidas totales
  - Lecciones activas
  - Críticas analizadas
- ✅ **Resumen de evolución** (tarjeta destacada):
  - Fecha de última síntesis
  - Focos actuales de aprendizaje
  - Score promedio de últimos 10 cuentos
- ✅ **Barra de progreso** hacia próxima síntesis automática
- ✅ **Lista de lecciones** con:
  - Título y descripción
  - Categoría (ritmo, vocabulario, engagement, etc.)
  - Estado (activa, archivada, en revisión)
  - Fecha de síntesis
  - Ejemplos de aplicación
- ✅ **Filtros dinámicos:**
  - Por categoría (pacing, vocabulary, engagement, etc.)
  - Por estado (active, under-review, archived)
- ✅ **Visualización de archivos JSON:**
  - **Ver Learning History** - Muestra learning_history.json completo
  - **Ver Style Profile** - Muestra style_profile.json completo
  - Copiar al portapapeles
  - Descargar como archivo .json
- ✅ **Acciones:**
  - Síntesis manual de lecciones
  - Actualizar datos en tiempo real
- ✅ **Diseño visual:**
  - Tarjetas con gradientes
  - Badges de estado
  - Mensajes de éxito/error
  - Visualizador JSON con formato

**URL:** `http://localhost:3000/aprendizaje.html`

**Flujo de uso:**
1. Ve estadísticas generales del sistema de aprendizaje
2. Observa resumen de evolución con métricas clave
3. Observa progreso hacia próxima síntesis (cada 2 críticas)
4. Filtra lecciones por categoría y estado
5. Explora cada lección con ejemplos de aplicación
6. **Haz clic en "Ver Learning History"** para ver el JSON completo
7. **Haz clic en "Ver Style Profile"** para ver la evolución del estilo
8. Copia o descarga los archivos JSON para análisis externo
9. Ejecuta síntesis manual si lo deseas
10. Navega entre generador, biblioteca y aprendizaje

**Endpoints consumidos:**
- `GET /learning/statistics` - Estadísticas del sistema
- `GET /learning/lessons?category=X&status_filter=Y` - Lista de lecciones
- `GET /learning/history` - Historial completo JSON
- `GET /learning/style-profile` - Perfil de estilo JSON
- `POST /learning/synthesize?last_n_critiques=2` - Síntesis manual

## 🎨 Estilos (styles.css)

Archivo único compartido por ambas páginas con:

- **Design System:**
  - Gradiente púrpura de fondo
  - Contenedor blanco con sombras
  - Tipografía: Segoe UI
  - Colores primarios: #667eea, #764ba2

- **Componentes:**
  - Formularios responsivos
  - Checkboxes personalizados
  - Tarjetas de cuentos con hover effects
  - Spinner de carga animado
  - Navegación entre páginas
  - **Visualizador JSON** con syntax highlighting
  - **Botones de acción** para copiar/descargar templates

- **Responsive:** Diseñado para móvil y desktop (max-width: 800px)

## ⚙️ JavaScript

### **app.js** - Lógica del Generador

Funciones principales:
- `loadCharacters()` - Carga personajes del backend como checkboxes
- `generateStory()` - Envía request a `/stories/generate`
- `displayResults()` - Muestra el cuento recién generado
- `showError()` - Manejo de errores
- Validación de formulario
- Logging completo en consola

### **cuentos.js** - Lógica de la Biblioteca

Funciones principales:
- `toggleIllustrationTemplate()` - **NUEVO** Muestra/oculta plantilla de ilustraciones
- `copyTemplateToClipboard()` - **NUEVO** Copia JSON al portapapeles
- `downloadTemplate()` - **NUEVO** Descarga JSON como archivo
- `loadStoriesList()` - Obtiene todos los cuentos de `/stories`
- `showStoryDetails()` - Muestra vista detalle de un cuento
- `backToList()` - Vuelve a la lista desde detalle
- Estado vacío con botón a generador
- Logging completo en consola

### 🔍 Debugging con Logs

Ambos archivos JS incluyen logging detallado:

```javascript
console.log('[nombreFuncion] 🚀 Acción...');
console.log('[nombreFuncion] ✅ Éxito');
console.error('[nombreFuncion] ❌ Error');
```

**Abre la consola** (F12) para ver el flujo completo de ejecución.

## 🚀 Configuración

### Variables de Entorno

```javascript
// js/app.js y js/cuentos.js
const API_BASE_URL = 'http://127.0.0.1:8000';
```

Cambiar si el backend está en otro puerto/host.

### Servidor HTTP Simple

```bash
# Desde la raíz del proyecto
cd frontend
python -m http.server 3000

# O usar el script iniciar.ps1 que abre ambos servidores
.\iniciar.ps1
```

## 📡 Consumo de API

### Endpoints Utilizados

| Endpoint | Método | Archivo | Descripción |
|----------|--------|---------|-------------|
| `/characters` | GET | app.js | Cargar personajes para checkboxes |
| `/stories/generate` | POST | app.js | Generar nuevo cuento |
| `/stories?limit=20` | GET | cuentos.js | Listar cuentos guardados |

### Formato de Request - Generar Cuento

```json
{
  "theme": "Una aventura en el bosque",
  "character_names": ["Martín"] | null,
  "moral_lesson": "La importancia de la amistad" | null,
  "target_age": 6,
  "length": "medium",
  "special_elements": "Incluye magia" | null
}
```

### Formato de Response - Cuento Generado

```json
{
  "id": "uuid",
  "title": "Título del cuento",
  "content": "Contenido completo...",
  "version": 1,,
  "illustration_template": {
    "cuento_metadata": {
      "titulo": "...",
      "estilo_visual": "...",
      "configuracion_color": {...}
    },
    "composicion_diseno": {
      "ilustraciones_superiores": {...},
      "ilustracion_principal": {...}
    }
  }
}
```

**Nota:** `illustration_template` solo está presente en cuentos nuevos (generados después de la actualización)created_at": "2026-02-04T10:30:00",
  "prompt_used": "Prompt usado..."
}
```

## 🎯 Navegación entre Páginas

```
┌─────────────────────────┐
│   index.html            │  ← Crear cuentos
│  [📚 Ver Guardados →]   │
└─────────────────────────┘
           │
           ▼
┌─────────────────────────┐
│   cuentos.html          │  ← Ver biblioteca
│  [← Crear Nuevo]        │
└─────────────────────────┘
```

- **Desde generador:** Link arriba a la derecha
- **Desde biblioteca:** Link arriba a la izquierda

## ✨ Características Destacadas

### Formulario Flexible
- ✅ **Solo tema obligatorio** - Mínima fricción
- ✅ **Personajes opcionales** - 0, 1 o múltiples
- ✅ **Sin personajes** → IA crea los suyos
- ✅ **Con personajes** → Integrados en la historia

### UX Optimizada
- ⚡ Loading spinner durante generación
- 📱 Diseño responsive
- 🎨 Transiciones suaves
- ⌨️ Validación en tiempo real
- 🔄 Auto-scroll al resultado

### Manejo de Errores
- ✅ Mensajes claros y amigables
- ✅ Validación de campos
- ✅ Verificación de conectividad
- ✅ Logging detallado en consola

## 🐛 Debugging

### Consola del Navegador (F12)

Logs disponibles con emojis para fácil lectura:

```
🎬 [DOMContentLoaded] Aplicación iniciada
[loadCharacters] Iniciando carga de personajes...
[loadCharacters] Response status: 200
[loadCharacters] Personajes recibidos: [...]
✅ [loadCharacters] Personajes cargados exitosamente
```

### Problemas Comunes

**Error: "No se pueden cargar personajes"**
- Verificar que backend esté corriendo en puerto 8000
- Revisar CORS en backend
- Ver consola para detalles

**Error: "Error al generar cuento"**
- Verificar GEMINI_API_KEY en backend/.env
- Revisar logs del backend
- Ver consola para error específico

**Cuentos no se muestran en biblioteca**
- Verificar que hay cuentos en la base de datos
- Revisar endpoint GET /stories
- Ver logs en consola

## 📦 Dependencias

### Cero Dependencias Externas

El frontend es **vanilla JavaScript** puro:
- ✅ Sin frameworks (React, Vue, Angular)
- ✅ Sin librerías (jQuery, Lodash)
- ✅ Sin bundlers (Webpack, Vite)
- ✅ Solo HTML5 + CSS3 + ES6+

**Ventajas:**
- 🚀 Extremadamente rápido
- 📦 Ligero (< 50KB total)
- 🔧 Fácil de mantener
- 🎯 Sin build process

## 🔄 Flujo de Datos

```
Usuario → Formulario → app.js
                         ↓
              POST /stories/generate
                         ↓
              Backend (Gemini IA)
                         ↓
              Response (JSON)
                         ↓
              displayResults()
                         ↓
              DOM actualizado
```

## 🎨 Personalización

### Cambiar Colores

Editar en `css/styles.css`:

```css
/* Gradiente de fondo */
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);

/* Color primario */
color: #667eea;
```

### Cambiar Límite de Cuentos

Editar en `js/cuentos.js`:

```javascript
const response = await fetch(`${API_BASE_URL}/stories?limit=20`);
//                                                        ^^^^ Cambiar aquí
```

## 📝 Próximas Mejoras

- [ ] Paginación en biblioteca de cuentos
- [ ] Búsqueda y filtros
- [ ] Edición de cuentos guardados
- [ ] Compartir cuentos (export PDF/texto)
- [ ] Favoritos/marcadores
- [ ] Modo oscuro
- [ ] Animaciones de transición
- [ ] PWA (Progressive Web App)

## 🤝 Contribuir

Para modificar el frontend:

1. Editar archivos HTML/CSS/JS
2. Refrescar navegador (no requiere build)
3. Ver cambios inmediatamente
4. Usar consola para debugging

## 📄 Licencia

Parte del proyecto CuentaCuentos AI.
