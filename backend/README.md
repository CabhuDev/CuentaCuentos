# Backend - CuentaCuentos AI

Este directorio contiene el **backend API REST** del proyecto, desarrollado con **FastAPI**.

## 🏗️ Arquitectura y Estado

La aplicación sigue una arquitectura modular y está en estado **completamente funcional**.

- ✅ **API REST modular** con FastAPI (`routers` y `services`).
- ✅ **Integración completa con Google Gemini** para generación, crítica y síntesis.
- ✅ **Bucle de Aprendizaje Evolutivo** implementado y activo.
- ✅ **Sistema RAG (Retrieval-Augmented Generation)** implementado y activo.
- ✅ **Base de datos dual:** SQLite para desarrollo y preparada para PostgreSQL en producción.
- ✅ **Documentación de API automática** en `/docs` (Swagger) y `/redoc`.

Para una visión completa de la arquitectura del sistema, consulta el documento principal: **[🏗️ `docs/architecture.md`](../docs/architecture.md)**.

## 🚀 Instalación y Ejecución

Las instrucciones detalladas para la configuración del entorno y la ejecución del proyecto se encuentran en la raíz:

- **Guía de Inicio Rápido:** **[🚀 `README.md`](../README.md)**
- **Guía para Contribuidores:** **[🤝 `CONTRIBUTING.md`](../CONTRIBUTING.md)**

Una vez en marcha, puedes verificar la salud del backend en `http://localhost:8000/health`.

## 🗃️ Base de Datos

- **Desarrollo (Por defecto):** Se utiliza **SQLite**. El archivo `cuentacuentos.db` se creará en este mismo directorio.
- **Producción (Opcional):** La aplicación está preparada para usar **PostgreSQL** con la extensión `pgvector`. Para ello, modifica la variable `DATABASE_URL` en tu archivo `.env`.

## 📋 API Endpoints Principales

La API está completamente documentada en la interfaz de Swagger (`/docs`). Los endpoints más importantes son:

- `POST /stories/generate`: Genera un cuento, lo guarda, y dispara el ciclo de crítica y aprendizaje.
- `GET /stories`: Lista todos los cuentos guardados.
- `GET /characters`: Lista los personajes disponibles.
- `GET /learning/statistics`: Muestra estadísticas sobre el proceso de aprendizaje de la IA.
- `GET /learning/lessons`: Lista las lecciones que la IA ha aprendido.
- `GET /rag/search`: Endpoint de prueba para la funcionalidad de búsqueda semántica (RAG).

## 🛡️ Autenticación de Usuarios

El backend ahora incluye un sistema de autenticación de usuarios basado en **JWT (JSON Web Tokens)** implementado con **FastAPI** y **PyJWT**.

### Configuración Necesaria

1.  **`SECRET_KEY` en `.env`**:
    Debes añadir una clave secreta fuerte y única en tu archivo `.env`. Puedes generarla con `openssl rand -hex 32`.
    ```
    SECRET_KEY='TU_CLAVE_SECRETA_GENERADA_AQUI'
    ```

2.  **Tabla `users` en la Base de Datos**:
    Asegúrate de que la tabla `users` exista en tu base de datos `cuentacuentos.db` (para SQLite) o en tu base de datos de producción. Puedes crearla con el siguiente comando SQL:
    ```sql
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        hashed_password TEXT NOT NULL
    );
    ```

### Endpoints de Autenticación

Los endpoints de autenticación están disponibles en la raíz de la API (no bajo `/api`) y son:

-   `POST /users/`
    *   **Descripción**: Registra un nuevo usuario en el sistema.
    *   **Body de la solicitud (JSON)**:
        ```json
        {
            "username": "nombre_de_usuario",
            "password": "tu_contraseña_segura"
        }
        ```
    *   **Respuesta**: Devuelve los datos del usuario registrado (sin la contraseña).

-   `POST /token`
    *   **Descripción**: Permite a un usuario iniciar sesión y obtener un token de acceso JWT.
    *   **Body de la solicitud (Form Data - `application/x-www-form-urlencoded`)**:
        *   `username`: El nombre de usuario.
        *   `password`: La contraseña del usuario.
    *   **Respuesta (JSON)**:
        ```json
        {
            "access_token": "eyJhbGciOiJIUzI1Ni...",
            "token_type": "bearer"
        }
        ```
        El `access_token` debe ser incluido en las solicitudes a endpoints protegidos.

-   `GET /users/me`
    *   **Descripción**: Un endpoint de ejemplo para verificar que la autenticación funciona. Devuelve la información del usuario actualmente autenticado.
    *   **Cabeceras de la solicitud**: Requiere la cabecera `Authorization`.
        *   `Authorization`: `Bearer TU_ACCES_TOKEN_AQUI` (reemplaza `TU_ACCES_TOKEN_AQUI` con el token obtenido de `/token`).

### Ejemplo de Uso (Python con `httpx`)

```python
import httpx

BASE_URL = "http://localhost:8000" # O la URL de tu despliegue

# 1. Registrar un nuevo usuario
register_data = {
    "username": "miusuario",
    "password": "micontraseñasegura"
}
response = httpx.post(f"{BASE_URL}/users/", json=register_data)
print("Registro:", response.json())

# 2. Iniciar sesión y obtener un token
login_data = {
    "username": "miusuario",
    "password": "micontraseñasegura"
}
response = httpx.post(
    f"{BASE_URL}/token",
    data=login_data,
    headers={"Content-Type": "application/x-www-form-urlencoded"}
)
token_response = response.json()
access_token = token_response.get("access_token")
print("Login:", token_response)

if access_token:
    # 3. Acceder a un endpoint protegido
    headers = {"Authorization": f"Bearer {access_token}"}
    response = httpx.get(f"{BASE_URL}/users/me", headers=headers)
    print("Usuario actual (protegido):", response.json())
else:
    print("No se pudo obtener el token de acceso.")
```