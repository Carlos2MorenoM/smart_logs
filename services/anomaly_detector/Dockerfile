FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos todo el código fuente
COPY ./src /app

EXPOSE 8001

# El comando por defecto será servir la API
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8001"]