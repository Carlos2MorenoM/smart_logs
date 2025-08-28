from fastapi import FastAPI, Request
import pika
import json

app = FastAPI()

@app.post("/ingest")
async def ingest_log(request: Request):
    """
    Receives log ingest request
    """
    try:
        log_data = await request.json()

        connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
        channel = connection.channel()

        channel.queue_declare(queue='logs', durable=True)

        channel.basic_publish(
            exchange='',
            routing_key='logs',
            body=json.dumps(log_data)
        )
        connection.close()

        return {"status": "success", "message": "Log received and sent to queue"}

    except Exception as e:
        return {"status": "error", "message": str(e)}