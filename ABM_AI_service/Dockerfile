# Imagen base
FROM python:3.12-slim

# Configuración de Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Directorio de trabajo
WORKDIR /app

# Instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copiar proyecto
COPY . .

# Usuario sin privilegios
RUN adduser --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

# Puerto
EXPOSE 8001

# Ejecutar aplicación
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]