# 🚀 Guía de Despliegue en VPS

Esta guía explica cómo desplegar CuentaCuentos en tu VPS paso a paso.

## 📋 Prerrequisitos

1. **Acceso SSH configurado** con claves públicas/privadas al VPS
2. **Docker y Docker Compose** instalados en el VPS
3. **Nginx** instalado y configurado con SSL en el VPS
4. **Archivo `.env`** configurado localmente en `backend/.env` con:
   ```
   GEMINI_API_KEY=tu_clave_aqui
   ELEVENLABS_API_KEY=tu_clave_aqui
   ```

## 🎯 Proceso de Despliegue

### Primera vez (Configuración Inicial)

Si es la **primera vez** que despliegas en el VPS, usa este script:

```powershell
.\setup-vps-inicial.ps1
```

Este script:
1. ✅ Crea el directorio `/var/www/cuentacuentos` en el VPS
2. ✅ Clona el repositorio desde GitHub
3. ✅ Copia tu archivo `.env` local al VPS
4. ✅ Verifica los archivos necesarios
5. ✅ Configura Nginx automáticamente
6. ✅ Levanta el contenedor Docker
7. ✅ Verifica el estado

### Despliegues Posteriores

Para actualizar el código después de la configuración inicial:

```powershell
.\deploy-cuentacuentos-backend.ps1
```

Este script:
1. ✅ Hace merge de `develop` a `main`
2. ✅ Sube los cambios a GitHub
3. ✅ Actualiza el código en el VPS con `git pull`
4. ✅ Reconstruye y reinicia el contenedor Docker
5. ✅ Verifica que el backend está funcionando

## 🌐 URLs de la Aplicación

Después del despliegue exitoso:

- **Frontend**: https://elratonsinverguencilla.es/cuentacuentos/
- **Documentación API**: https://elratonsinverguencilla.es/cuentacuentos/docs
- **Health Check**: https://elratonsinverguencilla.es/cuentacuentos/health

## 🐳 Configuración de Docker

El proyecto usa Docker Compose con:
- **Puerto**: 8002 (mapeado internamente a 8000)
- **Imagen**: Construida desde el Dockerfile local
- **Variables**: Cargadas desde `backend/.env`

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
**Solución**: 
```bash
ssh root@31.97.36.248
cd /var/www/cuentacuentos
docker-compose logs
```

### Error: "Can't find API key"
**Solución**: 
```bash
ssh root@31.97.36.248
nano /var/www/cuentacuentos/backend/.env
# Añade:
# GEMINI_API_KEY=tu_clave
# ELEVENLABS_API_KEY=tu_clave
docker-compose restart
```

### Verificar contenedor en ejecución
```bash
ssh root@31.97.36.248
docker ps | grep cuentacuentos
```

### Ver logs en tiempo real
```bash
ssh root@31.97.36.248
cd /var/www/cuentacuentos
docker-compose logs -f
```

### Recargar Nginx
```bash
ssh root@31.97.36.248
sudo nginx -t
sudo systemctl reload nginx
```

## 📂 Estructura en el VPS

```
/var/www/cuentacuentos/
├── backend/
│   ├── .env                    # Variables de entorno (API keys)
│   ├── main.py
│   ├── requirements.txt
│   └── ...
├── frontend/
│   ├── index.html
│   ├── cuentos.html
│   └── ...
├── deployment/
│   └── nginx_vps.conf         # Configuración de Nginx
├── docker-compose.yml          # Configuración de Docker
├── Dockerfile
└── ...
```

## 🔐 Seguridad

⚠️ **IMPORTANTE**: 
- Nunca subas el archivo `.env` a GitHub
- Las API keys solo deben estar en el servidor
- El archivo `.env` está en `.gitignore`

## 📊 Estado Actual del VPS

Consulta [docs/VPS-ESTADO-2026-02-06.md](./VPS-ESTADO-2026-02-06.md) para ver:
- Contenedores en ejecución
- Puertos ocupados
- Configuración actual de Nginx
- Servicios disponibles

## 📞 Soporte

Si tienes problemas:
1. Revisa los logs: `docker-compose logs`
2. Verifica el estado: `docker ps -a`
3. Comprueba nginx: `sudo nginx -t`
4. Consulta la documentación en `/docs`
