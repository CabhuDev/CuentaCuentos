# Guía de Contribución para CuentaCuentos AI

¡Gracias por tu interés en contribuir a CuentaCuentos AI! Toda ayuda es bienvenida. Esta guía contiene las directrices para contribuir de forma efectiva y segura.

## 🚀 Cómo Empezar

Para empezar a desarrollar, necesitas tener el backend y el frontend funcionando en tu máquina local.

### 1. Configuración del Entorno

La forma más sencilla de poner en marcha todo el proyecto es usando el script de PowerShell proporcionado en la raíz:

```powershell
# Desde la raíz del proyecto, ejecuta el script:
.\iniciar.ps1
```

Este script se encarga de:
1.  Activar el entorno virtual de Python (`.venv`).
2.  Instalar las dependencias de `requirements.txt` si es necesario.
3.  Iniciar el servidor del **backend** en `http://localhost:8000`.
4.  Iniciar un servidor simple para el **frontend** en `http://localhost:3000`.

### 2. Configuración Manual

Si prefieres levantar cada parte por separado:

#### Backend
```powershell
# 1. Navega a la carpeta del backend
cd backend

# 2. Activa el entorno virtual
.\.venv\Scripts\Activate.ps1

# 3. Asegúrate de tener las dependencias
pip install -r requirements.txt

# 4. Copia el archivo de configuración de ejemplo
Copy-Item .env.example .env

# 5. Añade tus API Keys en el archivo .env
# GEMINI_API_KEY=tu_clave_de_gemini_aqui
# SECRET_KEY=tu_clave_secreta_para_jwt  # Genera una con: openssl rand -hex 32
# ELEVENLABS_API_KEY=tu_clave_de_elevenlabs_aqui  # Opcional, para TTS
# BREVO_API_KEY=tu_clave_de_brevo_aqui  # Opcional, para emails de reset

# 6. Inicia el servidor
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

#### Frontend
```powershell
# 1. En una terminal separada, navega a la carpeta del frontend
cd frontend

# 2. Levanta un servidor de desarrollo
python -m http.server 3000
```

## 🎨 Estilo de Código y Convenciones

- **Backend:** El backend sigue una arquitectura modular con `services` para la lógica de negocio y `routers` para los endpoints. Por favor, mantén esta separación.
- **Frontend:** El frontend es "vanilla" (HTML, CSS, JS) sin frameworks. El código debe ser claro y estar bien comentado.
- **General:** Usa nombres de variables y funciones descriptivos en inglés o español, manteniendo la consistencia con el código circundante.

## 🧪 Pruebas

Actualmente, el proyecto está en proceso de añadir una suite de tests automatizados con `pytest`. Si añades una nueva funcionalidad crítica al backend, por favor, considera añadir también un test que la cubra en el directorio `backend/tests/`.

Para ejecutar los tests existentes:
```powershell
# Desde la carpeta 'backend' (con el entorno virtual activado)
pytest
```

---

## 🔒 Directrices de Seguridad y Commits

**Esta es la parte más importante de la guía.** Proteger las claves de API es fundamental.

### Checklist Rápido ANTES de cada `git push`

```powershell
# 1. Revisa qué archivos has modificado
git status

# 2. Confirma que NO veas archivos sensibles en la lista de cambios, como:
#    - backend/.env
#    - backend/*.db
#    - backend/.venv/
#    - __pycache__/

# 3. Si todo está en orden, añade tus cambios
git add .

# 4. Escribe un mensaje de commit descriptivo
git commit -m "feat: Añade nueva funcionalidad de ..."

# 5. Sube tus cambios
git push origin main
```

### ¿Qué hacer si añades un archivo sensible por error?

Si accidentalmente añades un archivo como `.env` al "staging area", quítalo antes de hacer commit:

```powershell
# Quitar un archivo específico del staging
git reset HEAD backend/.env

# Quitar todos los archivos del staging para empezar de nuevo
git reset
```

### 🆘 ¡He subido una clave de API a GitHub!

Si esto ocurre, la clave se considera comprometida.

1.  **REVOCA LA CLAVE INMEDIATAMENTE:** Ve a tu [Google AI Studio](https://aistudio.google.com/app/apikey) y elimina o regenera la clave expuesta.
2.  **ACTUALIZA TU `.env` LOCAL:** Usa la nueva clave para seguir trabajando.
3.  **LIMPIA EL HISTORIAL DE GIT:** Este es un paso avanzado. Si no estás seguro, pide ayuda. Puedes encontrar instrucciones detalladas en `docs/security.md`.

Para más información, consulta la **[Guía de Seguridad Completa](docs/security.md)**.
