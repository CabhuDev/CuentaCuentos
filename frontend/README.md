# Frontend - CuentaCuentos AI

Este directorio contiene la interfaz web para el proyecto CuentaCuentos AI. Es un cliente ligero que consume la API REST del backend para proporcionar una experiencia de usuario interactiva.

## 📦 Filosofía: Cero Dependencias

El frontend está construido intencionadamente con **JavaScript, HTML y CSS puros (vanilla)**.

- ✅ **Sin frameworks** (React, Vue, Angular)
- ✅ **Sin librerías** (jQuery, Lodash)
- ✅ **Sin bundlers** (Webpack, Vite)

Esto lo hace extremadamente ligero, rápido y fácil de mantener sin necesidad de un proceso de `build`.

## 🏗️ Estructura de Archivos

```
frontend/
├── index.html          # 📝 Generador de cuentos (página principal)
├── cuentos.html        # 📚 Biblioteca de cuentos guardados
├── aprendizaje.html    # 🧠 Dashboard del sistema de aprendizaje
├── css/
│   └── styles.css      # 🎨 Estilos compartidos para todas las páginas
└── js/
    ├── app.js          # ⚙️ Lógica para la página de generación
    └── cuentos.js      # 📖 Lógica para la biblioteca de cuentos
```

## 📄 Páginas

1.  **`index.html` (Generador):** Permite a los usuarios crear nuevos cuentos, especificando un tema, personajes y otras características.
2.  **`cuentos.html` (Biblioteca):** Muestra todos los cuentos generados y guardados en la base de datos, permitiendo ver sus detalles y la plantilla para ilustraciones.
3.  **`aprendizaje.html` (Dashboard):** Ofrece una vista en tiempo real de cómo el sistema de IA está aprendiendo, mostrando estadísticas, lecciones aprendidas y el progreso general.

## 🚀 Ejecución

Las instrucciones detalladas para la configuración del entorno y la ejecución del proyecto se encuentran en la raíz:

- **Guía de Inicio Rápido:** **[🚀 `README.md`](../README.md)**
- **Guía para Contribuidores:** **[🤝 `CONTRIBUTING.md`](../CONTRIBUTING.md)**

Para iniciar el servidor de desarrollo del frontend, puedes usar el script `iniciar.ps1` en la raíz del proyecto o ejecutar `python -m http.server 3000` desde esta carpeta.
