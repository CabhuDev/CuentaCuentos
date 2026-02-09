// ─── API Client para CuentaCuentos AI ───
// En desarrollo: Vite proxy redirige /api, /token, /users a http://127.0.0.1:8000
// En producción: las rutas son relativas a /cuentacuentos

const getBaseUrl = () => (import.meta.env.DEV ? '' : '/cuentacuentos');

function getToken() {
  return localStorage.getItem('cuentacuentos_token');
}

function authHeaders() {
  const token = getToken();
  const headers = {};
  if (token) headers['Authorization'] = `Bearer ${token}`;
  return headers;
}

async function handleResponse(res) {
  if (!res.ok) {
    let detail = `Error ${res.status}`;
    try {
      const data = await res.json();
      detail = data.detail || detail;
    } catch {
      /* ignore parse errors */
    }
    console.error('[API] ❌ Error en respuesta:', detail);
    throw new Error(detail);
  }
  return res.json();
}

// ─── Auth ────────────────────────────────────────────

export async function login(username, password) {
  console.log('[login] 🔐 Iniciando login para usuario:', username);
  const base = getBaseUrl();
  const body = new URLSearchParams();
  body.append('username', username);
  body.append('password', password);

  const res = await fetch(`${base}/token`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body,
  });
  console.log('[login] Response status:', res.status);
  const result = await handleResponse(res);
  console.log('[login] ✅ Login exitoso');
  return result;
}

export async function register(username, password, email) {
  console.log('[register] 📝 Registrando usuario:', username, email ? `con email: ${email}` : 'sin email');
  const base = getBaseUrl();
  const body = { username, password };
  if (email) body.email = email;
  const res = await fetch(`${base}/users/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  console.log('[register] Response status:', res.status);
  const result = await handleResponse(res);
  console.log('[register] ✅ Registro exitoso');
  return result;
}

export async function getMe() {
  console.log('[getMe] 👤 Obteniendo perfil de usuario...');
  const base = getBaseUrl();
  const res = await fetch(`${base}/users/me`, {
    headers: authHeaders(),
  });
  console.log('[getMe] Response status:', res.status);
  const result = await handleResponse(res);
  console.log('[getMe] ✅ Perfil obtenido:', result.username);
  return result;
}

// ─── Password Management ─────────────────────────────

export async function changePassword(currentPassword, newPassword) {
  console.log('[changePassword] 🔑 Solicitando cambio de contraseña...');
  const base = getBaseUrl();
  const res = await fetch(`${base}/change-password`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...authHeaders() },
    body: JSON.stringify({ current_password: currentPassword, new_password: newPassword }),
  });
  console.log('[changePassword] Response status:', res.status);
  const result = await handleResponse(res);
  console.log('[changePassword] ✅ Contraseña cambiada');
  return result;
}

export async function forgotPassword(email) {
  console.log('[forgotPassword] 📧 Solicitando reset de contraseña para:', email);
  const base = getBaseUrl();
  const res = await fetch(`${base}/forgot-password`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email }),
  });
  console.log('[forgotPassword] Response status:', res.status);
  const result = await handleResponse(res);
  console.log('[forgotPassword] ✅ Solicitud enviada');
  return result;
}

export async function resetPassword(token, newPassword) {
  console.log('[resetPassword] 🔐 Reseteando contraseña con token...');
  const base = getBaseUrl();
  const res = await fetch(`${base}/reset-password`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ token, new_password: newPassword }),
  });
  console.log('[resetPassword] Response status:', res.status);
  const result = await handleResponse(res);
  console.log('[resetPassword] ✅ Contraseña reseteada');
  return result;
}

// ─── Stories ─────────────────────────────────────────

export async function generateStory(data) {
  console.log('[generateStory] 🚀 Generando cuento con tema:', data.theme);
  console.log('[generateStory] Parámetros:', data);
  const base = getBaseUrl();
  const res = await fetch(`${base}/api/stories/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...authHeaders() },
    body: JSON.stringify(data),
  });
  console.log('[generateStory] Response status:', res.status);
  const result = await handleResponse(res);
  console.log('[generateStory] ✅ Cuento generado:', result.title);
  return result;
}

export async function getStories(limit = 20) {
  console.log('[getStories] 📚 Cargando cuentos guardados (limit:', limit + ')...');
  const base = getBaseUrl();
  const res = await fetch(`${base}/api/stories?limit=${limit}`, {
    headers: authHeaders(),
  });
  console.log('[getStories] Response status:', res.status);
  const result = await handleResponse(res);
  console.log('[getStories] ✅ Cuentos recibidos:', result.length, 'cuentos');
  return result;
}

export async function getStory(id) {
  const base = getBaseUrl();
  const res = await fetch(`${base}/api/stories/${id}`, {
    headers: authHeaders(),
  });
  return handleResponse(res);
}

export async function getStoryCritiques(id) {
  const base = getBaseUrl();
  const res = await fetch(`${base}/api/stories/${id}/critiques`, {
    headers: authHeaders(),
  });
  return handleResponse(res);
}

// ─── Characters ──────────────────────────────────────

export async function getCharacters() {
  console.log('[getCharacters] 🎭 Cargando personajes disponibles...');
  const base = getBaseUrl();
  const res = await fetch(`${base}/api/characters`, {
    headers: authHeaders(),
  });
  console.log('[getCharacters] Response status:', res.status);
  const result = await handleResponse(res);
  console.log('[getCharacters] ✅ Personajes recibidos:', result.length, 'personajes');
  return result;
}

// ─── Audio ───────────────────────────────────────────

export async function generateAudio(storyId, texto) {
  console.log('[generateAudio] 🎵 Generando audio para cuento ID:', storyId);
  const base = getBaseUrl();
  const res = await fetch(`${base}/api/audio/cuentos/${storyId}/generar`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...authHeaders() },
    body: JSON.stringify({ texto, cuento_id: storyId }),
  });
  console.log('[generateAudio] Response status:', res.status);
  const result = await handleResponse(res);
  console.log('[generateAudio] ✅ Audio generado:', result.audio_url);
  return result;
}

export async function checkAudioExists(storyId) {
  const base = getBaseUrl();
  try {
    const res = await fetch(`${base}/api/audio/cuentos/${storyId}/estado`, {
      headers: authHeaders(),
    });
    if (!res.ok) return { existe: false };
    return res.json();
  } catch {
    return { existe: false };
  }
}

export async function deleteAudio(storyId) {
  const base = getBaseUrl();
  const res = await fetch(`${base}/api/audio/cuentos/${storyId}`, {
    method: 'DELETE',
    headers: authHeaders(),
  });
  return handleResponse(res);
}

export function getFullAudioUrl(audioUrl) {
  if (!audioUrl) return '';
  if (audioUrl.startsWith('http')) return audioUrl;
  const base = getBaseUrl();
  return `${base}${audioUrl}`;
}

// ─── Learning ────────────────────────────────────────

export async function getLearningStats() {
  const base = getBaseUrl();
  const res = await fetch(`${base}/api/learning/statistics`, {
    headers: authHeaders(),
  });
  return handleResponse(res);
}

export async function getLessons(category, statusFilter) {
  const base = getBaseUrl();
  const params = new URLSearchParams();
  if (category) params.append('category', category);
  if (statusFilter) params.append('status_filter', statusFilter);
  const qs = params.toString();
  const res = await fetch(`${base}/api/learning/lessons${qs ? '?' + qs : ''}`, {
    headers: authHeaders(),
  });
  return handleResponse(res);
}

export async function synthesizeLessons(lastN = 5) {
  const base = getBaseUrl();
  const res = await fetch(
    `${base}/api/learning/synthesize?last_n_critiques=${lastN}`,
    { method: 'POST', headers: authHeaders() }
  );
  return handleResponse(res);
}

export async function getLearningHistory() {
  console.log('[getLearningHistory] 📜 Obteniendo learning history...');
  const base = getBaseUrl();
  const res = await fetch(`${base}/api/learning/history`, {
    headers: authHeaders(),
  });
  console.log('[getLearningHistory] Response status:', res.status);
  const result = await handleResponse(res);
  console.log('[getLearningHistory] ✅ History recibido');
  return result;
}

export async function getStyleProfile() {
  console.log('[getStyleProfile] 🎨 Obteniendo style profile...');
  const base = getBaseUrl();
  const res = await fetch(`${base}/api/learning/style-profile`, {
    headers: authHeaders(),
  });
  console.log('[getStyleProfile] Response status:', res.status);
  const result = await handleResponse(res);
  console.log('[getStyleProfile] ✅ Profile recibido');
  return result;
}

// ─── RAG ─────────────────────────────────────────────

export async function getRAGStats() {
  console.log('[getRAGStats] 🔍 Obteniendo estadísticas RAG...');
  const base = getBaseUrl();
  const res = await fetch(`${base}/api/rag/stats`, {
    headers: authHeaders(),
  });
  console.log('[getRAGStats] Response status:', res.status);
  const result = await handleResponse(res);
  console.log('[getRAGStats] ✅ Stats RAG recibidos:', result);
  return result;
}
