# 1. Imagen base oficial de Python
FROM python:3.12-slim

# 2. Configuración de Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. Directorio de trabajo
WORKDIR /app

# 4. Instalación de dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# 5. Copia de código
COPY . .

# 6. Usuario de seguridad
RUN adduser --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

# 7. Puerto
EXPOSE 8000

# 8. Ejecución
CMD ["sh", "-c", "exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}"]