FROM python:3.10-slim

WORKDIR /app

COPY scripts/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./data /app/data
COPY ./scripts/ingest_logs.py .

CMD ["python", "ingest_logs.py"]
