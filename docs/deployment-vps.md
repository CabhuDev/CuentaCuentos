# 🚀 Guía de Despliegue en VPS

Esta guía explica cómo desplegar CuentaCuentos en tu VPS paso a paso, incluyendo el entorno de desarrollo local con Docker.

## 📋 Prerrequisitos

### En tu máquina local
1. **Docker Desktop** instalado y funcionando
2. **Git** configurado con acceso al repositorio
3. **Node.js 20+** (solo para desarrollo local sin Docker)
4. **Python 3.11+** (solo para desarrollo del backend sin Docker)
5. **Archivo `.env`** configurado en `backend/.env`:
   ```
   GEMINI_API_KEY=tu_clave_aqui
   ELEVENLABS_API_KEY=tu_clave_aqui
   SECRET_KEY=tu_clave_secreta_jwt
   BREVO_API_KEY=tu_clave_brevo
   ```

### En el VPS
1. **Acceso SSH configurado** con claves públicas/privadas
2. **Docker y Docker Compose** instalados
3. **Nginx** instalado y configurado con SSL (Let's Encrypt)

---

## 🏗️ Arquitectura de Despliegue

```
VPS (elratonsinverguencilla.es)
├── Nginx (80/443) ─── SSL Let's Encrypt
│   ├── /cuentacuentos/     → Proxy a contenedor frontend (localhost:8003)
│   ├── /cuentacuentos/api/ → Proxy a contenedor backend (localhost:8002)
│   └── /cuentosparacrecer/ → Otro proyecto (sin cambios)
│
├── Docker: cuentacuentos_backend   (8002 → 8000 interno) ── FastAPI + SQLite
├── Docker: cuentacuentos_frontend  (8003 → 80 interno)   ── Nginx + React SPA
└── Docker: otros contenedores (obratec, pablo-cabello, etc.)
```

### Puertos en uso

| Puerto | Servicio | Contenedor |
|--------|----------|------------|
| 80/443 | Nginx (host) | - |
| 3000 | Obratec App | obratec-app |
| 5678 | n8n | obratec-n8n |
| 8001 | Cuentos Para Crecer API | cuentos_fastapi |
| **8002** | **CuentaCuentos Backend** | cuentacuentos_backend |
| **8003** | **CuentaCuentos Frontend** | cuentacuentos_frontend |
| 8080 | Pablo Cabello Web | pablo-cabello-web |

---

## 🖥️ Desarrollo Local

### Opción A: Solo Frontend (desarrollo rápido)

Ideal para cambios de UI sin tocar el backend.

```powershell
# Terminal 1: Backend local con Python
cd backend
pip install -r requirements.txt
uvicorn main:app --reload

# Terminal 2: Frontend con Hot Reload (Vite dev server)
cd frontend-react
npm install
npm run dev
```

Accede a `http://localhost:3000`. Vite redirige las peticiones API a `http://127.0.0.1:8000` automáticamente.

### Opción B: Docker Compose (simula producción)

Ideal para verificar que todo funciona antes de desplegar.

```powershell
# Levantar ambos contenedores
docker-compose up --build

# O solo el frontend (si el backend ya corre localmente)
docker-compose up --build --no-deps frontend
```

| Servicio | URL Local | Puerto |
|----------|-----------|--------|
| Frontend React | http://localhost:8003 | 8003 |
| Backend API | http://localhost:8002 | 8002 |
| API Docs | http://localhost:8002/docs | 8002 |

### Opción C: Solo frontend Docker (sin backend Docker)

```powershell
docker-compose up --build --no-deps frontend
```

El frontend se sirve en `http://localhost:8003` pero no tendrá backend a menos que lo lances con `uvicorn` aparte.

### Verificar build local

```powershell
# Construir sin levantar
docker-compose build frontend

# Verificar que el contenedor responde
docker-compose up -d --no-deps frontend
curl http://localhost:8003/          # → 200 (index.html)
curl http://localhost:8003/login     # → 200 (SPA routing OK)

# Limpiar
docker-compose down
```

---

## 🎯 Proceso de Despliegue en VPS

### Primera vez (Configuración Inicial)

```powershell
.\setup-vps-inicial.ps1
```

Este script:
1. ✅ Crea el directorio `/var/www/cuentacuentos` en el VPS
2. ✅ Clona el repositorio desde GitHub
3. ✅ Copia tu archivo `.env` local al VPS
4. ✅ Verifica los archivos necesarios
5. ✅ Configura Nginx automáticamente
6. ✅ Levanta los contenedores Docker (backend + frontend)
7. ✅ Verifica el estado

**Importante:** La primera vez debes actualizar manualmente la configuración de Nginx en el VPS para usar la versión React (proxy al contenedor frontend):
```bash
ssh root@31.97.36.248
# Backup
cp /etc/nginx/sites-available/elratonsinverguencilla.es \
   /etc/nginx/sites-available/elratonsinverguencilla.es.backup

# Editar y reemplazar el bloque /cuentacuentos/ con el contenido de
# deployment/nginx_vps_react.conf
nano /etc/nginx/sites-available/elratonsinverguencilla.es

# Verificar y recargar
nginx -t && systemctl reload nginx
```

### Despliegues Posteriores

#### Actualizar Backend

```powershell
.\deploy-cuentacuentos-backend.ps1
```

Este script:
1. ✅ Hace merge de `develop` a `main`
2. ✅ Sube los cambios a GitHub
3. ✅ Actualiza el código en el VPS con `git pull`
4. ✅ Reconstruye y reinicia solo el contenedor `backend`
5. ✅ Limpia imágenes Docker antiguas
6. ✅ Verifica el health check

#### Actualizar Frontend React

```powershell
.\deploy-cuentacuentos-frontend.ps1
```

Este script:
1. ✅ Hace merge de `develop` a `main`
2. ✅ Sube los cambios a GitHub
3. ✅ Actualiza el código en el VPS con `git pull`
4. ✅ Reconstruye el contenedor `frontend` (multi-stage: Node build → Nginx serve)
5. ✅ Limpia imágenes Docker antiguas
6. ✅ Hace backup de Nginx y recarga configuración
7. ✅ Verifica que el frontend y backend responden

#### Actualizar Ambos

```powershell
.\deploy-cuentacuentos-backend.ps1
.\deploy-cuentacuentos-frontend.ps1
```

O manualmente:
```bash
ssh root@31.97.36.248 "cd /var/www/cuentacuentos && git pull origin main && docker-compose up -d --build"
```

---

## 🐳 Configuración de Docker

### docker-compose.yml

```yaml
services:
  backend:
    build: .                          # Dockerfile en raíz (Python FastAPI)
    container_name: cuentacuentos_backend
    ports:
      - "8002:8000"
    env_file:
      - ./backend/.env
    volumes:
      - ./backend:/app/backend        # Hot reload en desarrollo
    restart: unless-stopped

  frontend:
    build: ./frontend-react           # Multi-stage: Node build → Nginx serve
    container_name: cuentacuentos_frontend
    ports:
      - "8003:80"
    depends_on:
      - backend
    restart: unless-stopped
```

### Frontend Dockerfile (Multi-Stage)

```dockerfile
# Stage 1: Build con Node.js
FROM node:20-alpine AS build
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm ci --silent
COPY . .
RUN npm run build                     # Vite genera dist/ con base=/cuentacuentos/

# Stage 2: Serve con Nginx
FROM nginx:alpine
COPY nginx.conf /etc/nginx/conf.d/cuentacuentos.conf
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

El Nginx interno del contenedor maneja:
- SPA routing (try_files → index.html)
- Cache de assets de Vite (1 año, immutable)
- Compresión gzip
- No-cache para index.html (siempre la última versión)

### Nginx del VPS (host)

El Nginx del host actúa como reverse proxy hacia los contenedores:

```nginx
# Frontend React → contenedor Docker (puerto 8003)
location /cuentacuentos/ {
    proxy_pass http://127.0.0.1:8003/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    ...
}

# API Backend → contenedor Docker (puerto 8002)
location /cuentacuentos/api/ {
    rewrite /cuentacuentos/api/(.*) /api/$1 break;
    proxy_pass http://127.0.0.1:8002;
    ...
}
```

La configuración completa está en `deployment/nginx_vps_react.conf`.

---

## 🌐 URLs de la Aplicación

Después del despliegue exitoso:

| URL | Descripción |
|-----|-------------|
| https://elratonsinverguencilla.es/cuentacuentos/ | Frontend React |
| https://elratonsinverguencilla.es/cuentacuentos/api/ | API REST |
| https://elratonsinverguencilla.es/cuentacuentos/docs | Documentación Swagger |
| https://elratonsinverguencilla.es/cuentacuentos/health | Health Check |

---

## 🔧 Solución de Problemas

### Error: "No such file or directory: /var/www/cuentacuentos"
**Solución**: Ejecuta `setup-vps-inicial.ps1` primero

### Error: "KeyError: 'ContainerConfig'" o problemas al recrear contenedor
**Causa**: Contenedor corrupto o en mal estado  
**Solución**: 
```powershell
.\limpiar-vps.ps1
.\deploy-cuentacuentos-backend.ps1
```

El script `limpiar-vps.ps1`:
- Detiene todos los contenedores de CuentaCuentos
- Elimina volúmenes huérfanos
- Limpia imágenes y cachés de Docker
- Deja el VPS listo para un despliegue limpio

### Error: "Backend unhealthy"
```bash
ssh root@31.97.36.248
cd /var/www/cuentacuentos
docker-compose logs backend
```

### Error: El frontend muestra página en blanco
```bash
# Verificar que el contenedor frontend está corriendo
ssh root@31.97.36.248 "docker ps | grep cuentacuentos_frontend"

# Ver logs del frontend
ssh root@31.97.36.248 "cd /var/www/cuentacuentos && docker-compose logs frontend"

# Verificar que Nginx hace proxy al puerto correcto (8003)
ssh root@31.97.36.248 "curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:8003/"
```

### Error: "Can't find API key"
```bash
ssh root@31.97.36.248
nano /var/www/cuentacuentos/backend/.env
# Añade las claves necesarias
docker-compose restart backend
```

### Verificar contenedores en ejecución
```bash
ssh root@31.97.36.248
docker ps | grep cuentacuentos
# Debería mostrar:
# cuentacuentos_backend   ... 8002->8000  Up ...
# cuentacuentos_frontend  ... 8003->80    Up ...
```

### Ver logs en tiempo real
```bash
ssh root@31.97.36.248
cd /var/www/cuentacuentos
docker-compose logs -f                    # Todos
docker-compose logs -f backend            # Solo backend
docker-compose logs -f frontend           # Solo frontend
```

### Recargar Nginx
```bash
ssh root@31.97.36.248
sudo nginx -t
sudo systemctl reload nginx
```

### Rebuild completo (nuclear option)
```bash
ssh root@31.97.36.248
cd /var/www/cuentacuentos
docker-compose down --remove-orphans
docker system prune -f
docker-compose up -d --build
```

---

## 📂 Estructura en el VPS

```
/var/www/cuentacuentos/
├── backend/
│   ├── .env                    # Variables de entorno (API keys) - NO en git
│   ├── main.py
│   ├── requirements.txt
│   ├── data/
│   │   ├── cuentacuentos.db    # Base de datos SQLite
│   │   └── audio/              # Archivos de audio generados
│   └── ...
├── frontend-react/
│   ├── Dockerfile              # Multi-stage build
│   ├── nginx.conf              # Nginx interno del contenedor
│   ├── src/                    # Código fuente React
│   └── ...
├── deployment/
│   ├── nginx_vps.conf          # Config Nginx (frontend estático - legacy)
│   └── nginx_vps_react.conf    # Config Nginx (frontend Docker - ACTUAL)
├── docker-compose.yml          # Orquestación: backend + frontend
├── Dockerfile                  # Backend (Python/FastAPI)
└── ...
```

---

## 🔐 Seguridad

⚠️ **IMPORTANTE**: 
- Nunca subas el archivo `.env` a GitHub
- Las API keys solo deben estar en el servidor
- El archivo `.env` está en `.gitignore`
- El backend solo escucha en localhost (no expuesto directamente)
- Todo el tráfico externo pasa por Nginx con SSL

---

## 📊 Workflow de Desarrollo

```
1. Desarrollar en rama 'develop'
   ↓
2. Probar localmente:
   - Frontend: npm run dev (hot reload)
   - Docker: docker-compose up --build (simula producción)
   ↓
3. Commit y push a 'develop'
   ↓
4. Desplegar:
   .\deploy-cuentacuentos-frontend.ps1  (solo frontend)
   .\deploy-cuentacuentos-backend.ps1   (solo backend)
   ↓
5. El script hace merge develop → main, push, y
   reconstruye contenedores en VPS automáticamente
```
