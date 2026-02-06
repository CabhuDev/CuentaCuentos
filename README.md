# CuentaCuentos AI: Sistema de Generación Evolutiva de Cuentos

Bienvenido a CuentaCuentos AI, un motor de escritura de cuentos infantiles que utiliza IA para generar historias y aprende de sí mismo para mejorar su calidad narrativa con el tiempo.

## ✨ Características Principales

- **Generación Inteligente:** Crea cuentos para niños de 2 a 6 años con coherencia narrativa y visual.
- **Aprendizaje Evolutivo:** Implementa un ciclo de **Generar → Criticar → Sintetizar → Aplicar** para mejorar continuamente.
- **Calidad Literaria Profesional:** Aplica 6 técnicas de la literatura infantil para crear cuentos memorables y enriquecedores.
- **Generación Aumentada por Recuperación (RAG):** Utiliza cuentos exitosos del pasado como inspiración para mejorar las nuevas creaciones.
- **Arquitectura API-First:** Backend y frontend desacoplados para mayor escalabilidad y mantenibilidad.
- **Personajes Persistentes:** Mantiene la consistencia de los personajes a través de múltiples historias.

---

## 🚀 Inicio Rápido

La forma más sencilla de poner en marcha todo el proyecto (backend y frontend) es usando el script de PowerShell.

```powershell
# Desde la raíz del proyecto, ejecuta el script:
.\iniciar.ps1
```

Este script se encargará de:
1.  Activar el entorno virtual de Python.
2.  Instalar las dependencias si es necesario.
3.  Iniciar el servidor del **backend** en `http://localhost:8000`.
4.  Iniciar el servidor del **frontend** en `http://localhost:3000`.

Una vez ejecutado, podrás acceder a:
- **🎨 Generador de Cuentos:** `http://localhost:3000`
- **📚 API Docs (Swagger):** `http://localhost:8000/docs`

### Configuración Manual

Si prefieres un inicio manual, sigue las guías detalladas en:
- 📖 **[Guía del Backend](backend/README.md)**
- 📖 **[Guía del Frontend](frontend/README.md)**

---

## 📚 Estructura de la Documentación

Este `README` es solo la puerta de entrada. Para entender el proyecto a fondo, consulta los siguientes documentos:

| Archivo | Descripción |
|---|---|
| 🎯 **[`PROJECT_STATUS.md`](PROJECT_STATUS.md)** | **Estado actual del proyecto y roadmap futuro.** ¡Empieza aquí! |
| 🏗️ **[`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)** | **Visión general de la arquitectura,** incluyendo el bucle de aprendizaje. |
| 🎭 **[`docs/LITERARY_QUALITY.md`](docs/LITERARY_QUALITY.md)** | Detalla las **6 técnicas de escritura profesional** que usa la IA. |
| 🔄 **[`BUCLE-APRENDIZAJE.md`](BUCLE-APRENDIZAJE.md)** | Explicación **a fondo** de cómo funciona el sistema de auto-mejora. |
| 🔒 **[`docs/SECURITY.md`](docs/SECURITY.md)** | **Guía de seguridad obligatoria** sobre el manejo de API keys. |
| 🔧 **[`backend/README.md`](backend/README.md)** | Guía detallada para configurar y ejecutar el **backend**. |
| 🎨 **[`frontend/README.md`](frontend/README.md)** | Guía detallada para configurar y ejecutar el **frontend**. |

---

## 📄 Licencia

Este proyecto está licenciado bajo la **MIT License**. Para más detalles, consulta el archivo [LICENSE](LICENSE).

