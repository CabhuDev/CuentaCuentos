# CuentaCuentos AI — Frontend React

> Interfaz de usuario moderna construida con **React 19 + Vite 6**, que consume la API REST del backend FastAPI. Incluye gestión de usuarios (registro/login con JWT), generación de cuentos con IA, biblioteca, audio narrado y sistema de aprendizaje.

---

## Índice

- [Stack Tecnológico](#stack-tecnológico)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Arquitectura General](#arquitectura-general)
- [Configuración de Vite](#configuración-de-vite)
- [Sistema de Autenticación](#sistema-de-autenticación)
- [Cliente API](#cliente-api)
- [Componentes](#componentes)
- [Páginas](#páginas)
- [Rutas](#rutas)
- [Estilos CSS](#estilos-css)
- [Despliegue en Producción (VPS)](#despliegue-en-producción-vps)
- [Comandos de Desarrollo](#comandos-de-desarrollo)
- [Integración con el Backend](#integración-con-el-backend)

---

## Stack Tecnológico

| Tecnología             | Versión   | Propósito                                |
|------------------------|-----------|------------------------------------------|
| React                  | ^19.0.0   | Librería UI (componentes funcionales)    |
| React DOM              | ^19.0.0   | Renderizado en el navegador              |
| React Router DOM       | ^6.28.0   | Enrutamiento SPA (client-side routing)   |
| Vite                   | ^6.1.0    | Bundler y servidor de desarrollo         |
| @vitejs/plugin-react   | ^4.3.4    | Plugin de Vite para JSX/React            |

> **Sin dependencias adicionales**: No se usa Redux, Axios ni otras librerías externas. El estado global se maneja con React Context y las peticiones HTTP con `fetch` nativo.

---

## Estructura del Proyecto

```
frontend-react/
├── index.html                  # HTML raíz (punto de entrada de Vite)
├── package.json                # Dependencias y scripts npm
├── vite.config.js              # Configuración de Vite (proxy, base URL)
├── .gitignore                  # Exclusiones (node_modules, dist, .env)
└── src/
    ├── main.jsx                # Entry point: React, Router, AuthProvider
    ├── App.jsx                 # Definición de rutas (Routes/Route)
    ├── index.css               # Estilos globales (~1100 líneas)
    ├── api/
    │   └── client.js           # Cliente API completo (todas las llamadas HTTP)
    ├── context/
    │   └── AuthContext.jsx     # Context de autenticación (login, register, logout)
    ├── components/
    │   ├── Layout.jsx          # Layout principal (header, nav, outlet)
    │   ├── Pagination.jsx      # Componente de paginación reutilizable
    │   ├── ProtectedRoute.jsx  # Wrapper de rutas protegidas
    │   ├── Spinner.jsx         # Indicador de carga reutilizable
    │   └── StoryCard.jsx       # Tarjeta de cuento para la biblioteca
    └── pages/
        ├── ForgotPassword.jsx  # Solicitar reset de contraseña por email
        ├── Generator.jsx       # Generador de cuentos (formulario + resultado)
        ├── Learning.jsx        # Dashboard de aprendizaje (stats, lecciones, filtros)
        ├── Library.jsx         # Biblioteca de cuentos guardados (paginada)
        ├── Login.jsx           # Página de inicio de sesión
        ├── Profile.jsx         # Perfil de usuario y cambio de contraseña
        ├── Register.jsx        # Página de registro (con email opcional)
        ├── ResetPassword.jsx   # Restablecer contraseña con token del email
        └── StoryDetail.jsx     # Detalle de cuento (audio, ilustraciones, críticas)
```

---

## Arquitectura General

```
┌─────────────────────────────────────────────────────┐
│                     NAVEGADOR                        │
│                                                      │
│  ┌────────────┐   ┌──────────────┐   ┌───────────┐ │
│  │  React     │──▶│ AuthContext   │──▶│ API Client│ │
│  │  Router    │   │ (JWT Token)  │   │ (fetch)   │ │
│  │  (SPA)     │   └──────────────┘   └─────┬─────┘ │
│  └────────────┘                            │        │
└────────────────────────────────────────────┼────────┘
                                             │
                    ┌────────────────────────┼────────────────┐
                    │        Servidor / VPS                    │
                    │                                          │
                    │  [Nginx]  ──▶  /cuentacuentos/          │
                    │     │          (archivos estáticos SPA)  │
                    │     │                                    │
                    │     ├──▶  /cuentacuentos/api/*           │
                    │     ├──▶  /cuentacuentos/token           │
                    │     └──▶  /cuentacuentos/users/*         │
                    │              │                            │
                    │              ▼                            │
                    │     [Docker :8002 → :8000]               │
                    │     [FastAPI Backend]                     │
                    │     [SQLite + Gemini AI]                  │
                    └──────────────────────────────────────────┘
```

---

## Configuración de Vite

Archivo: `vite.config.js`

### Base URL Dinámica

```javascript
base: mode === 'production' ? '/cuentacuentos/' : '/'
```

- **Desarrollo** (`/`): Las rutas son relativas a la raíz.
- **Producción** (`/cuentacuentos/`): Coincide con la ruta del dominio donde se sirve la app.

### Proxy para Desarrollo

En modo desarrollo (`npm run dev`), Vite redirige automáticamente las peticiones API al backend local:

| Ruta          | Destino                     | Propósito                          |
|---------------|-----------------------------|------------------------------------|
| `/api`        | `http://127.0.0.1:8000`    | Endpoints de la API REST           |
| `/token`      | `http://127.0.0.1:8000`    | Login (obtener JWT)                |
| `/users`      | `http://127.0.0.1:8000`    | Registro y perfil de usuario       || `/forgot-password` | `http://127.0.0.1:8000` | Solicitar reset de contraseña    |
| `/reset-password`  | `http://127.0.0.1:8000` | Resetear contraseña con token    |
| `/change-password` | `http://127.0.0.1:8000` | Cambiar contraseña (autenticado) || `/health`     | `http://127.0.0.1:8000`    | Health check                       |
| `/data/audio` | `http://127.0.0.1:8000`    | Archivos de audio estáticos        |

> **Nota**: El backend debe estar corriendo en el puerto 8000 para que el proxy funcione: `uvicorn main:app --reload`

### Puerto del servidor de desarrollo

Configurado en el puerto **3000** (`server.port: 3000`).

---

## Sistema de Autenticación

### Archivo: `src/context/AuthContext.jsx`

El sistema de autenticación está implementado con **React Context** y maneja todo el ciclo de vida de la sesión del usuario.

### Flujo de Autenticación

```
                    ┌───────────────┐
                    │  App se monta  │
                    └───────┬───────┘
                            │
                    ┌───────▼───────┐
                    │ ¿Hay token en │
                    │ localStorage? │
                    └───────┬───────┘
                       Sí /   \ No
                         /     \
              ┌─────────▼┐   ┌─▼──────────┐
              │GET /users │   │ loading=   │
              │   /me     │   │ false      │
              └─────┬─────┘   │ user=null  │
                    │         └──────┬─────┘
              ┌─────▼─────┐         │
              │ ¿Válido?   │         ▼
              └──┬─────┬──┘   Redirige a /login
            Sí /     \ No
              /       \
    ┌────────▼──┐   ┌──▼────────┐
    │ user=data │   │ Borra     │
    │ loading=  │   │ token y   │
    │ false     │   │ user=null │
    └───────────┘   └───────────┘
```

### Estado Proporcionado

| Propiedad   | Tipo       | Descripción                                    |
|-------------|------------|------------------------------------------------|
| `user`      | Object/null| Datos del usuario autenticado (`{id, username, email}`)|
| `loading`   | boolean    | `true` mientras se verifica el token al montar  |
| `login()`   | function   | `async (username, password)` → obtiene JWT y datos del usuario |
| `register()`| function   | `async (username, password, email?)` → registra + auto-login |
| `logout()`  | function   | Borra token y limpia estado                     |

### Hook de acceso

```jsx
import { useAuth } from './context/AuthContext'

const { user, loading, login, register, logout } = useAuth()
```

### Almacenamiento del Token

- **Clave en localStorage**: `cuentacuentos_token`
- **Formato**: JWT Bearer Token
- **Verificación automática**: Al montar la app, si existe un token, se valida contra `GET /users/me`
- **Expiración**: Si el backend rechaza el token, se borra automáticamente

---

## Cliente API

### Archivo: `src/api/client.js`

Todas las llamadas HTTP al backend están centralizadas en este módulo. Usa `fetch` nativo (no Axios).

### Funciones Exportadas

#### Autenticación

| Función       | Método/Ruta                | Parámetros               | Descripción                                    |
|---------------|----------------------------|--------------------------|------------------------------------------------|
| `login()`     | `POST /token`              | `username, password`     | Login con form-urlencoded, devuelve `{access_token}` |
| `register()`  | `POST /users/`             | `username, password, email?` | Crear usuario (JSON body), email opcional     |
| `getMe()`     | `GET /users/me`            | —                        | Obtener perfil del usuario autenticado          |

#### Gestión de Contraseñas

| Función            | Método/Ruta             | Parámetros                     | Descripción                                    |
|--------------------|-------------------------|--------------------------------|------------------------------------------------|
| `changePassword()` | `POST /change-password` | `currentPassword, newPassword` | Cambiar contraseña (requiere autenticación)     |
| `forgotPassword()` | `POST /forgot-password` | `email`                        | Solicitar reset por email (envía enlace Brevo)  |
| `resetPassword()`  | `POST /reset-password`  | `token, newPassword`           | Resetear contraseña con token del email         |

#### Cuentos

| Función              | Método/Ruta                       | Parámetros           | Descripción                                    |
|----------------------|-----------------------------------|----------------------|------------------------------------------------|
| `generateStory()`   | `POST /api/stories/generate`    | `{theme, character_names, moral_lesson, target_age, length, special_elements}` | Generar cuento con IA |
| `getStories()`      | `GET /api/stories?limit=N`      | `limit` (default 20) | Listar cuentos del usuario                     |
| `getStory()`        | `GET /api/stories/:id`          | `id`                 | Obtener cuento completo                        |
| `getStoryCritiques()`| `GET /api/stories/:id/critiques`| `id`                 | Obtener críticas de un cuento                  |

#### Personajes

| Función           | Método/Ruta           | Parámetros | Descripción                                    |
|-------------------|-----------------------|------------|------------------------------------------------|
| `getCharacters()` | `GET /api/characters` | —          | Listar personajes disponibles                  |

#### Audio (ElevenLabs TTS)

| Función              | Método/Ruta                              | Parámetros          | Descripción                                    |
|----------------------|------------------------------------------|---------------------|------------------------------------------------|
| `generateAudio()`   | `POST /api/audio/cuentos/:id/generar`   | `storyId, texto`    | Generar narración de audio con ElevenLabs      |
| `checkAudioExists()`| `GET /api/audio/cuentos/:id/estado`     | `storyId`           | Comprobar si existe audio para un cuento        |
| `deleteAudio()`     | `DELETE /api/audio/cuentos/:id`         | `storyId`           | Eliminar audio de un cuento                    |
| `getFullAudioUrl()` | — (helper local)                         | `audioUrl`          | Construir URL completa del archivo de audio     |

#### Aprendizaje

| Función                | Método/Ruta                              | Parámetros               | Descripción                                    |
|------------------------|------------------------------------------|--------------------------|------------------------------------------------|
| `getLearningStats()`   | `GET /api/learning/statistics`          | —                        | Obtener estadísticas de aprendizaje             |
| `getLessons()`         | `GET /api/learning/lessons`             | `category, statusFilter` | Listar lecciones con filtros opcionales         |
| `synthesizeLessons()`  | `POST /api/learning/synthesize`         | `lastN` (default 5)      | Sintetizar lecciones de las últimas N críticas   |

### Utilidades Internas

| Función           | Descripción                                                              |
|-------------------|--------------------------------------------------------------------------|
| `getBaseUrl()`    | Devuelve `''` en desarrollo (proxy maneja), `'/cuentacuentos'` en producción |
| `getToken()`      | Lee el JWT desde `localStorage`                                          |
| `authHeaders()`   | Genera `{ Authorization: 'Bearer <token>' }` si hay token               |
| `handleResponse()`| Parsea respuesta: si `!res.ok` lanza `Error` con `detail` del backend    |

### Manejo de Errores

Todas las funciones propagan errores como instancias de `Error` con el campo `detail` del backend:

```javascript
async function handleResponse(res) {
  if (!res.ok) {
    const data = await res.json();
    throw new Error(data.detail || `Error ${res.status}`);
  }
  return res.json();
}
```

---

## Componentes

### `Layout.jsx` — Layout Principal

Envuelve todas las páginas protegidas. Contiene:
- **Barra de navegación** con 3 enlaces: Generar (`/`), Cuentos (`/cuentos`), Aprendizaje (`/aprendizaje`)
- **Info del usuario** con nombre (clickable, lleva a `/perfil`) y botón "Salir"
- **Header** con título y subtítulo de la app
- **Outlet** de React Router para renderizar las páginas hijas
- Los enlaces activos se resaltan usando `NavLink` con la clase `.active`

### `Pagination.jsx` — Paginación Reutilizable

Componente presentacional reutilizable para paginación con estilo profesional.

| Prop           | Tipo       | Descripción                                    |
|----------------|------------|------------------------------------------------|
| `currentPage`  | number     | Página actual seleccionada                     |
| `totalPages`   | number     | Número total de páginas                        |
| `onPageChange` | function   | Callback al cambiar de página                   |
| `totalItems`   | number     | Total de elementos (para texto informativo)     |
| `itemsPerPage` | number     | Elementos por página (para texto informativo)   |

**Características**:
- Elipsis inteligente: muestra `1 ... 4 5 6 ... 10` cuando hay muchas páginas
- Botones Previous/Next con estados deshabilitados
- Página activa con gradiente púrpura
- Texto informativo: "Mostrando 1-12 de 47"
- Accesibilidad: `aria-label`, `aria-current`
- Responsive: se adapta a pantallas pequeñas

**Uso en**: Library.jsx (12 items/pág), Learning.jsx (8 items/pág)

### `ProtectedRoute.jsx` — Guardia de Rutas

Wrapper que protege las rutas que requieren autenticación:
- Si `loading === true` → muestra spinner con "Verificando sesión..."
- Si `user === null` → redirige a `/login`
- Si `user` existe → renderiza `<Outlet />` (las rutas hijas)

### `Spinner.jsx` — Indicador de Carga

Componente simple y reutilizable:
- Muestra una animación de spinner CSS
- Acepta prop `text` para mostrar mensaje debajo del spinner

### `StoryCard.jsx` — Tarjeta de Cuento

Tarjeta clickable usada en la biblioteca:
- Muestra título, fecha formateada, versión y preview (primeros 150 caracteres)
- Al hacer clic navega a `/cuentos/{id}`
- Fecha formateada en español (ej: "8 de febrero de 2026, 12:30")

---

## Páginas

### `Login.jsx` — Inicio de Sesión

| Campo     | Tipo     | Validación   |
|-----------|----------|--------------|
| Usuario   | text     | required     |
| Contraseña| password | required     |

**Comportamiento**:
- Formulario controlado con `useState`
- Al enviar: llama `auth.login()` → redirige a `/` si éxito
- Muestra errores del backend en `<div className="error">`
- Botón se deshabilita durante la petición
- Enlace a `/olvide-contrasena` para recuperar contraseña
- Enlace a `/registro` en la parte inferior

---

### `Register.jsx` — Registro de Usuario

| Campo              | Tipo     | Validación                  |
|--------------------|----------|-----------------------------||
| Usuario            | text     | required                    |
| Email              | email    | opcional (para reset de contraseña) |
| Contraseña         | password | required, min 4 caracteres  |
| Confirmar contraseña| password | required, debe coincidir    |

**Comportamiento**:
- Validación del lado del cliente:
  - Contraseña mínimo 4 caracteres
  - Las contraseñas deben coincidir
- El campo email es opcional, pero necesario para poder recuperar la contraseña
- Al enviar: llama `auth.register(username, password, email?)` → auto-login → redirige a `/`
- Enlace a `/login` en la parte inferior

---

### `Generator.jsx` — Generador de Cuentos

Formulario principal para generar cuentos con IA.

| Campo                | Tipo               | Obligatorio | Descripción                           |
|----------------------|--------------------|-------------|---------------------------------------|
| Tema                 | text input         | **Sí**      | Tema o escena del cuento              |
| Personajes           | checkboxes         | No          | Selección múltiple de personajes      |
| Lección moral        | text input         | No          | Enseñanza a transmitir                |
| Edad objetivo        | number (3-12)      | No          | Edad del público (default: 6)         |
| Longitud             | select             | No          | `short` / `medium` / `long`          |
| Elementos especiales | textarea           | No          | Elementos adicionales a incluir       |

**Comportamiento**:
- Al montar, carga personajes disponibles desde `GET /api/characters`
- Los personajes se muestran como checkboxes con nombre y edad aparente
- Al enviar, llama `generateStory()` con los datos del formulario
- Muestra spinner con "Creando tu cuento mágico..." durante la generación
- Al completar, muestra el título, contenido y enlace "Ver en la biblioteca →"

---

### `Library.jsx` — Biblioteca de Cuentos

Lista todos los cuentos del usuario.

**Comportamiento**:
- Al montar, carga hasta 50 cuentos con `getStories(50)`
- Muestra cada cuento como una `StoryCard` en una cuadrícula
- **Paginación**: 12 cuentos por página con componente `Pagination`
- Scroll automático al inicio al cambiar de página
- Estado vacío: icono 📚 + mensaje + botón para crear primer cuento
- Muestra el contador total: "📚 Biblioteca de Cuentos (N)"

---

### `StoryDetail.jsx` — Detalle de Cuento

Vista completa de un cuento individual con todas sus funcionalidades.

**Secciones**:

1. **Header**: Título, fecha y versión del cuento
2. **Audio**: Controles de audio (generar narración / reproductor / eliminar)
3. **Contenido**: Texto completo del cuento
4. **Plantilla de Ilustraciones**: JSON con prompts para IA de imágenes (toggle + copiar)
5. **Críticas**: Lista de críticas automáticas con score y texto

**Controles de Audio**:
- Si no hay audio → botón "🎵 Generar Narración en Audio" (llama a ElevenLabs TTS)
- Si hay audio → reproductor `<audio>` con controles nativos + botón eliminar
- Feedback de estado: ✅ generado (chars usados, duración) / ❌ error
- Confirmación antes de eliminar

**Plantilla de Ilustraciones**:
- Solo visible si el cuento tiene `illustration_template`
- Botón toggle "🎨 Ver/Ocultar Plantilla de Ilustraciones"
- Muestra JSON formateado en `<pre>`
- Botón "📋 Copiar JSON" copia al portapapeles

**Carga paralela**:
- Cuento y estado del audio se cargan en paralelo con `Promise.all`
- Las críticas se cargan en segundo plano sin bloquear

---

### `Learning.jsx` — Sistema de Aprendizaje

Dashboard completo del sistema de aprendizaje evolutivo.

**Secciones**:

1. **Estadísticas (stats-grid)**:
   | Tarjeta            | Campo API                |
   |---------------------|--------------------------|
   | Score Promedio       | `stats.average_score`    |
   | Total Lecciones     | `stats.total_lessons`    |
   | Cuentos Generados   | `stats.total_stories`    |
   | Críticas             | `stats.total_critiques`  |

2. **Acciones**:
   - Botón "🧠 Sintetizar Lecciones" → llama `synthesizeLessons(5)` → muestra resultado
   - Botón "🔄 Actualizar" → recarga datos

3. **Filtros**:
   | Filtro    | Opciones                                                                        |
   |-----------|---------------------------------------------------------------------------------|
   | Categoría | Todas, pacing, language choice, narrative structure, character development, emotional depth, sensory details |
   | Estado    | Todos, Activas, Archivadas                                                     |

4. **Lista de Lecciones**:
   Cada tarjeta muestra:
   - `insight` o título de la lección
   - Badge de estado (`active`/`archived`)
   - Categoría, prioridad, veces aplicada
   - `actionable_guidance` (descripción)
   - `supporting_evidence` (evidencia)

**Comportamiento**:
- Los filtros recargan los datos automáticamente (efecto dependiente de `filterCategory` y `filterStatus`)
- **Paginación**: 8 lecciones por página con componente `Pagination` (reset a pág.1 al cambiar filtros)
- Estado vacío con mensaje explicativo

5. **Estadísticas del Sistema RAG**:
   | Tarjeta            | Campo API                          |
   |--------------------|------------------------------------|
   | Cuentos Totales    | `ragStats.total_stories`           |
   | Con Embeddings     | `ragStats.stories_with_embeddings` |
   | Cobertura          | `ragStats.coverage_percentage`     |
   | Estado RAG         | `ragStats.ready_for_rag`           |

6. **Datos del Sistema**:
   - Resumen de Evolución (última síntesis, focos actuales, score promedio)
   - Botón "Ver Learning History" (carga lazy, muestra JSON con copiar/descargar)
   - Botón "Ver Style Profile" (carga lazy, muestra JSON con copiar/descargar)

---

### `Profile.jsx` — Perfil de Usuario

Página de perfil del usuario autenticado.

**Secciones**:

1. **Tarjeta de perfil**:
   - Avatar circular con inicial del username
   - Nombre de usuario y email
   - Aviso si no tiene email configurado (necesario para reset)

2. **Cambio de contraseña**:
   | Campo               | Tipo     | Validación                  |
   |---------------------|----------|-----------------------------|
   | Contraseña actual    | password | required                    |
   | Nueva contraseña     | password | required, min 6 caracteres  |
   | Confirmar nueva      | password | required, debe coincidir    |

   - Indicador visual de fortaleza (🔴 Débil / 🟡 Media / 🟢 Fuerte)
   - Validación: nueva contraseña diferente a la actual
   - Llama `POST /change-password` con token JWT
   - Mensaje de éxito/error al completar

---

### `ForgotPassword.jsx` — Recuperar Contraseña

Página pública (sin autenticación) para solicitar reset de contraseña.

| Campo | Tipo  | Validación |
|-------|-------|------------|
| Email | email | required   |

**Comportamiento**:
- Envía `POST /forgot-password` con el email
- Siempre muestra mensaje de éxito (por seguridad, no revela si el email existe)
- Vista de confirmación: icono 📧 + instrucciones + enlace a login
- Indica que el enlace expira en 1 hora
- Enlace para volver a login

---

### `ResetPassword.jsx` — Restablecer Contraseña

Página pública que se accede desde el enlace del email.

| Campo               | Tipo     | Validación                  |
|---------------------|----------|-----------------------------|
| Nueva contraseña     | password | required, min 6 caracteres  |
| Confirmar contraseña | password | required, debe coincidir    |

**Comportamiento**:
- Lee el `token` desde los query params de la URL (`?token=xxx`)
- Si no hay token: muestra error "Enlace inválido" + enlace para solicitar nuevo
- Si hay token: formulario de nueva contraseña con indicador de fortaleza
- Envía `POST /reset-password` con token + nueva contraseña
- Vista de éxito: icono ✅ + enlace a login
- Maneja errores de token expirado o inválido

---

## Rutas

```
┌────────────────────┬──────────────────┬─────────────┬──────────────────────┐
│ Ruta               │ Componente       │ Protegida   │ Descripción            │
├────────────────────┼──────────────────┼─────────────┼──────────────────────┤
│ /login             │ Login            │ No          │ Inicio de sesión      │
│ /registro          │ Register         │ No          │ Crear cuenta           │
│ /olvide-contrasena │ ForgotPassword   │ No          │ Solicitar reset email  │
│ /reset-password    │ ResetPassword    │ No          │ Restablecer con token  │
│ /                  │ Generator        │ Sí          │ Generar cuentos        │
│ /cuentos           │ Library          │ Sí          │ Biblioteca (paginada)  │
│ /cuentos/:id       │ StoryDetail      │ Sí          │ Detalle de cuento      │
│ /aprendizaje       │ Learning         │ Sí          │ Dashboard aprendizaje  │
│ /perfil            │ Profile          │ Sí          │ Perfil y cambio pass   │
│ /*                 │ → Redirect a /   │ —           │ Fallback (catch-all)   │
└────────────────────┴──────────────────┴─────────────┴──────────────────────┘
```

### Jerarquía de rutas

```
<Routes>
  ├── /login                    → <Login />
  ├── /registro                 → <Register />
  ├── /olvide-contrasena        → <ForgotPassword />
  ├── /reset-password           → <ResetPassword />
  ├── <ProtectedRoute>          (verifica autenticación)
  │   └── <Layout>              (header + nav + outlet)
  │       ├── /                 → <Generator />
  │       ├── /cuentos          → <Library />
  │       ├── /cuentos/:id      → <StoryDetail />
  │       ├── /aprendizaje      → <Learning />
  │       └── /perfil           → <Profile />
  └── /*                        → Navigate to /
</Routes>
```

### Basename dinámico

En `main.jsx`, el `BrowserRouter` recibe un `basename` basado en `import.meta.env.BASE_URL`:
- **Desarrollo**: `basename = '/'`
- **Producción**: `basename = '/cuentacuentos'`

Esto permite que React Router funcione correctamente bajo el subpath `/cuentacuentos/`.

---

## Estilos CSS

### Archivo: `src/index.css` (~1100 líneas)

Hoja de estilos global que mantiene la identidad visual del frontend original (HTML/CSS/JS vanilla).

### Diseño Visual

- **Fondo**: Gradiente diagonal `#667eea → #764ba2` (purple gradient)
- **Contenedor**: Fondo blanco, bordes redondeados (15px), sombra
- **Tipografía**: Segoe UI, Tahoma, Geneva, Verdana, sans-serif
- **Colores principales**: `#667eea` (azul-púrpura), `#764ba2` (púrpura)

### Secciones del CSS

| Sección                 | Descripción                                      |
|-------------------------|--------------------------------------------------|
| Reset & Base            | Box-sizing, body reset                           |
| Layout Principal        | `.app-background`, `.container`                   |
| Auth Pages              | `.auth-container`, `.auth-switch`                 |
| Header & Nav            | `.app-header`, `.nav-links`, `.nav-link`, `.user-info` |
| Formularios             | Inputs, selects, textareas, checkboxes, botones   |
| Resultados              | `.result-section`, `.story-title`, `.story-text`  |
| Biblioteca              | `.stories-list`, `.story-card`, `.empty-state`    |
| Story Detail            | `.story-detail`, `.back-button`, `.story-meta`    |
| Audio                   | `.audio-controls-container`, `.audio-player`      |
| Ilustraciones           | `.illustration-template-container`, `.json-display`|
| Críticas                | `.critique-content`, `.critique-item`             |
| Aprendizaje             | `.stats-grid`, `.filters-section`, `.lesson-card` |
| Paginación              | `.pagination-container`, `.pagination-btn`, `.pagination-ellipsis` |
| Utilidades              | `.spinner`, `.loading-indicator`, `.error`, `.success-message` |
| Responsive              | Media queries para ≤600px                         |
| Perfil de Usuario       | `.profile-card`, `.profile-avatar`, `.profile-section` |
| Fortaleza Contraseña    | `.password-strength`, `.strength-bar`, `.strength-fill` |
| Reset Password          | `.reset-success`, `.reset-hint`, `.btn-back-login` |

### Responsive Design

Breakpoint principal en `max-width: 600px`:
- Navegación apilada verticalmente
- Formularios en columna única
- Grid de estadísticas en 2 columnas (en lugar de 4)
- Contenedor con padding reducido (15px)
- Tarjetas de cuento en columna única

---

## Despliegue en Producción (VPS)

### Configuración Nginx: `deployment/nginx_vps_react.conf`

Reemplaza la configuración `nginx_vps.conf` del frontend vanilla.

### Diferencias respecto al frontend vanilla

| Aspecto                | Frontend Vanilla            | Frontend React                    |
|------------------------|-----------------------------|-----------------------------------|
| Tipo de aplicación     | Múltiples HTML estáticos    | SPA (Single Page Application)     |
| Routing                | Cada página es un .html     | React Router (client-side)        |
| try_files              | Estándar                    | Fallback a `index.html`           |
| Assets                 | Rutas fijas                 | Hash en filename (Vite build)     |
| Cache                  | Estándar                    | `immutable, 1y` para /assets/    |
| Auth endpoints         | No necesarios               | `/token` y `/users` proxied       |

### Pasos de despliegue

```bash
# 1. Construir el frontend
cd frontend-react
npm run build

# 2. Copiar dist/ al servidor
scp -r dist/* root@31.97.36.248:/var/www/cuentacuentos/frontend/

# 3. Actualizar configuración nginx (si es primera vez)
# Reemplazar el bloque de nginx_vps.conf con nginx_vps_react.conf

# 4. Recargar nginx
sudo nginx -t && sudo systemctl reload nginx
```

### Location blocks (Nginx)

| Location                          | Destino                               | Descripción                    |
|-----------------------------------|---------------------------------------|--------------------------------|
| `/cuentacuentos/`                 | `/var/www/cuentacuentos/frontend/`    | SPA con fallback a index.html  |
| `/cuentacuentos/assets/`          | mismo directorio                      | Cache inmutable (1 año)        |
| `/cuentacuentos/data/audio/`      | `backend/data/audio/`                 | Archivos de audio              |
| `/cuentacuentos/token`            | `proxy → :8002`                       | Endpoint de login              |
| `/cuentacuentos/users`            | `proxy → :8002`                       | Registro y perfil              |
| `/cuentacuentos/api/*`            | `proxy → :8002`                       | API REST completa              |
| `/cuentacuentos/docs`             | `proxy → :8002/docs`                  | Swagger UI                     |
| `/cuentacuentos/redoc`            | `proxy → :8002/redoc`                 | ReDoc                          |
| `/cuentacuentos/health`           | `proxy → :8002/health`               | Health check                   |

---

## Comandos de Desarrollo

```bash
# Instalar dependencias
npm install

# Servidor de desarrollo (puerto 3000)
npm run dev

# Build de producción (genera dist/)
npm run build

# Preview del build de producción
npm run preview
```

### Requisitos previos (desarrollo local)

1. **Node.js** v18+ (probado con v24.5.0)
2. **Backend corriendo** en puerto 8000:
   ```bash
   cd ../backend
   uvicorn main:app --reload
   ```
3. Las variables de entorno del backend (API keys de Gemini, ElevenLabs, etc.) deben estar configuradas

---

## Integración con el Backend

### Endpoints del Backend Consumidos

```
Autenticación (rutas de nivel superior, sin prefijo /api):
  POST /token                           → OAuth2 login (form-urlencoded)
  POST /users/                          → Crear usuario (con email opcional)
  GET  /users/me                        → Perfil del usuario autenticado

Gestión de Contraseñas (rutas de nivel superior):
  POST /forgot-password                 → Solicitar reset por email (Brevo)
  POST /reset-password                  → Resetear contraseña con token
  POST /change-password                 → Cambiar contraseña (requiere JWT)

API REST (prefijo /api):
  POST /api/stories/generate            → Generar cuento con IA (Gemini)
  GET  /api/stories?limit=N             → Listar cuentos del usuario
  GET  /api/stories/:id                 → Obtener cuento por ID
  GET  /api/stories/:id/critiques       → Obtener críticas de un cuento

  GET  /api/characters                  → Listar personajes disponibles

  POST /api/audio/cuentos/:id/generar   → Generar audio con ElevenLabs
  GET  /api/audio/cuentos/:id/estado    → Comprobar si existe audio
  DELETE /api/audio/cuentos/:id         → Eliminar audio

  GET  /api/learning/statistics         → Estadísticas de aprendizaje
  GET  /api/learning/lessons            → Listar lecciones (con filtros)
  POST /api/learning/synthesize         → Sintetizar lecciones de críticas
  GET  /api/learning/history            → Learning history (JSON completo)
  GET  /api/learning/style-profile      → Style profile (JSON completo)

  GET  /api/rag/stats                   → Estadísticas del sistema RAG
```

### Formato de autenticación

- **Login**: `POST /token` con `Content-Type: application/x-www-form-urlencoded` (`username` y `password` como campos de formulario, **no JSON**)
- **Token**: Se envía como `Authorization: Bearer <token>` en todas las peticiones protegidas
- **Almacenamiento**: `localStorage.cuentacuentos_token`

### Campos del Formulario de Generación

```json
{
  "theme": "string (requerido)",
  "character_names": ["string"] | null,
  "moral_lesson": "string" | null,
  "target_age": 6,
  "length": "short | medium | long",
  "special_elements": "string" | null
}
```

### Respuesta del Backend (Cuento Generado)

```json
{
  "id": 1,
  "title": "El bosque mágico",
  "content": "Texto completo del cuento...",
  "version": 1,
  "created_at": "2026-02-08T12:30:00",
  "illustration_template": { ... }
}
```

---

## Notas Técnicas

### Decisiones de diseño

1. **Sin Redux/Zustand**: El estado global se limita a la autenticación, que se gestiona con Context. El resto del estado es local a cada página.
2. **Sin Axios**: `fetch` nativo cubre todas las necesidades. El helper `handleResponse()` centraliza el manejo de errores.
3. **Sin CSS-in-JS**: Se usa un único archivo CSS global para mantener la coherencia con el diseño original.
4. **Carga paralela**: En `StoryDetail`, el cuento y el estado del audio se cargan con `Promise.all` para reducir latencia.

### Compatibilidad de navegadores

- El build de Vite usa `browserslist` para generar código compatible con navegadores modernos.
- Se genera un único bundle JS y un archivo CSS (con hash para cache busting).

### Archivos generados por el build

```
dist/
├── index.html
└── assets/
    ├── index-[hash].js
    └── index-[hash].css
```

---

## Contribuciones

¡Nos encantaría recibir tus contribuciones! Si quieres mejorar este proyecto, por favor sigue estos pasos:

1.  Haz un fork del repositorio.
2.  Crea una nueva rama (`git checkout -b feature/nueva-funcionalidad`).
3.  Realiza tus cambios y asegúrate de que el código sigue los estándares del proyecto.
4.  Ejecuta las pruebas (si existen) y asegúrate de que pasan.
5.  Haz commit de tus cambios (`git commit -m 'feat: Añadir nueva funcionalidad X'`).
6.  Sube tu rama (`git push origin feature/nueva-funcionalidad`).
7.  Abre un Pull Request detallando los cambios.

---

## Licencia

Este proyecto está bajo la Licencia MIT. Consulta el archivo `LICENSE` para más detalles.
