# Usa una imagen oficial de Python como base
FROM python:3.11-slim

# Evita que Python guarde archivos .pyc y establece el modo sin buffer para logs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia primero el archivo de requisitos para aprovechar el caché de Docker
COPY backend/requirements.txt .

# Instala las dependencias
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copia todo el directorio del backend al contenedor
COPY ./backend /app/backend

# Establece el directorio de trabajo a la carpeta del backend
WORKDIR /app/backend

# Expone el puerto en el que se ejecutará la aplicación
EXPOSE 8000

# Comando para ejecutar la aplicación cuando se inicie el contenedor
# Usa 0.0.0.0 para que sea accesible desde fuera del contenedor
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
