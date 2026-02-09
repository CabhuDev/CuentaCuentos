# ======================================================================
#  Dockerfile para el Frontend React de CuentaCuentos
#  Multi-stage build: Node (build) → Nginx (serve)
# ======================================================================

# --- Stage 1: Build ---
FROM node:20-alpine AS build

WORKDIR /app

# Copiar archivos de dependencias primero (cache de Docker)
COPY package.json package-lock.json* ./

# Instalar dependencias
RUN npm ci --silent

# Copiar el resto del código fuente
COPY . .

# Construir la aplicación en modo producción
# Vite usará base: '/cuentacuentos/' gracias a mode=production
RUN npm run build

# --- Stage 2: Serve ---
FROM nginx:alpine

# Eliminar la configuración por defecto de Nginx
RUN rm /etc/nginx/conf.d/default.conf

# Copiar nuestra configuración personalizada de Nginx
COPY nginx.conf /etc/nginx/conf.d/cuentacuentos.conf

# Copiar los archivos construidos desde el stage anterior
COPY --from=build /app/dist /usr/share/nginx/html

# Exponer el puerto 80
EXPOSE 80

# Nginx se ejecuta en primer plano
CMD ["nginx", "-g", "daemon off;"]
