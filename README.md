# CuentaCuentos AI: Sistema de Generación Evolutiva de Cuentos

Bienvenido a CuentaCuentos AI, un motor de escritura de cuentos infantiles que utiliza IA para generar historias y aprende de sí mismo para mejorar su calidad narrativa con el tiempo.

## ✨ Características Principales

- **Generación Inteligente:** Crea cuentos para niños de 2 a 6 años con coherencia narrativa y visual.
- **Aprendizaje Evolutivo:** Implementa un ciclo de **Generar → Criticar → Sintetizar → Aplicar** para mejorar continuamente.
- **Calidad Literaria Profesional:** Aplica 6 técnicas de la literatura infantil para crear cuentos memorables.
- **Generación Aumentada por Recuperación (RAG):** Utiliza cuentos exitosos del pasado como inspiración para mejorar las nuevas creaciones.
- **Arquitectura API-First:** Backend y frontend desacoplados para mayor escalabilidad y mantenibilidad.
- **Personajes Persistentes:** Mantiene la consistencia de los personajes a través de múltiples historias.
- **Sistema de Autenticación:** Control de acceso con JWT y funcionalidad completa de reset/cambio de contraseñas.
- **Narración por Voz (TTS):** Convierte cuentos en audio con voces naturales mediante ElevenLabs.

---

## 🛠️ Tech Stack

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)
![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)

---

## 🚀 Getting Started

La forma más sencilla y recomendada de poner en marcha todo el proyecto (backend y frontend) es usando el script de PowerShell proporcionado.

### 1. Requisitos
- Python 3.9+
- Una clave de API de Google Gemini. Puedes obtenerla [aquí](https://aistudio.google.com/app/apikey).

### 2. Configuración
1.  Copia el archivo de configuración de ejemplo en la carpeta `backend`:
    ```powershell
    Copy-Item backend/.env.example backend/.env
    ```
2.  Abre el nuevo archivo `backend/.env` y añade tu clave de API:
    ```
    GEMINI_API_KEY=tu_clave_aqui
    ```

### 3. Ejecución
Ejecuta el script de inicio desde la raíz del proyecto:
```powershell
.\iniciar.ps1
```
Este script activará el entorno virtual, instalará las dependencias e iniciará ambos servidores.

Una vez ejecutado, podrás acceder a:
- **🎨 Generador de Cuentos:** `http://localhost:3000`
- **📚 API Docs (Swagger):** `http://localhost:8000/docs`

---

## 📚 Estructura de la Documentación

Este `README` es solo la puerta de entrada. Para entender el proyecto a fondo, consulta los siguientes documentos:

| Archivo | Descripción |
|---|---|
| � **[`docs/INDEX.md`](docs/INDEX.md)** | **Índice completo de toda la documentación** con búsqueda por temas. |
| 🗺️ **[`ROADMAP.md`](ROADMAP.md)** | **Estado actual del proyecto y funcionalidades futuras.** ¡Empieza aquí! |
| 📜 **[`CHANGELOG.md`](CHANGELOG.md)** | **Historial de cambios y versiones** del proyecto. |
| 🏗️ **[`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)** | **Visión general de la arquitectura,** incluyendo el bucle de aprendizaje. |
| 🎭 **[`docs/literary-quality.md`](docs/literary-quality.md)** | Detalla las **6 técnicas de escritura profesional** que usa la IA. |
| 🤝 **[`CONTRIBUTING.md`](CONTRIBUTING.md)** | **Guía para contribuir**, configurar el entorno y directrices de seguridad. |
| 🚀 **[`docs/deployment-vps.md`](docs/deployment-vps.md)** | Pasos para desplegar el proyecto en un **servidor de producción**. |
| 🔒 **[`docs/security.md`](docs/security.md)** | **Guía de seguridad obligatoria** sobre el manejo de API keys. |
| 🔉 **[`docs/guides/elevenlabs-tts.md`](docs/guides/elevenlabs-tts.md)** | Guía completa para la **integración de audio Text-to-Speech**. |
| 🔑 **[`docs/guides/password-reset.md`](docs/guides/password-reset.md)** | Sistema de **reset y cambio de contraseñas** con Brevo. |

---

## 🤝 Contribuir

Las contribuciones son bienvenidas. Si quieres ayudar a mejorar el proyecto, por favor, lee nuestra **[Guía de Contribución](CONTRIBUTING.md)** para empezar.

---

## 📄 Licencia

Este proyecto está licenciado bajo la **MIT License**. Para más detalles, consulta el archivo [LICENSE](LICENSE).

