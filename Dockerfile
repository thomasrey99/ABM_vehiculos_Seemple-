FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Dependencias de sistema que necesita el servicio de IA (opencv, pillow, torch)
RUN apt-get update && apt-get install -y --no-install-recommends \
        libgl1 \
        libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# ---------- Venv del backend ----------
RUN python -m venv /opt/venv-backend
COPY ABM_backend/requirements.txt /tmp/backend-requirements.txt
RUN /opt/venv-backend/bin/pip install --upgrade pip \
    && /opt/venv-backend/bin/pip install -r /tmp/backend-requirements.txt \
    && rm /tmp/backend-requirements.txt

# ---------- Venv del servicio de IA ----------
RUN python -m venv /opt/venv-ai
COPY ABM_AI_service/requirements.txt /tmp/ai-requirements.txt
RUN /opt/venv-ai/bin/pip install --upgrade pip \
    && /opt/venv-ai/bin/pip install -r /tmp/ai-requirements.txt \
    && rm /tmp/ai-requirements.txt

# ---------- Código de ambas apps ----------
COPY ABM_backend/ /app/backend/
COPY ABM_AI_service/ /app/ai-service/

COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh \
    # limpieza extra de cachés que puedan haberse generado al copiar
    && find /app -type d -name "__pycache__" -exec rm -rf {} + \
    && find /app -type f -name "*.pyc" -delete

# Usuario sin privilegios
RUN adduser --disabled-password --gecos "" appuser \
    && chown -R appuser:appuser /app /opt/venv-backend /opt/venv-ai
USER appuser

EXPOSE 8000 8001

CMD ["/app/start.sh"]