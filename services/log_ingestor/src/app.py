from fastapi import FastAPI, Request, HTTPException
from contextlib import asynccontextmanager
import pika
import json
import pika.spec

# --- RabbitMQ Global Connection ---
# We use global variables to hold a single, long-lived connection and channel.
# This avoids the massive overhead of connecting/disconnecting on every HTTP request.
rabbitmq_connection = None
rabbitmq_channel = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manages the RabbitMQ connection lifecycle, aligned with the application's startup
    and shutdown events. This is the recommended modern approach in FastAPI.
    """
    global rabbitmq_connection, rabbitmq_channel
    print("Attempting to connect to RabbitMQ...")
    try:
        # Establish the connection once when the application starts.
        rabbitmq_connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='rabbitmq', heartbeat=600, blocked_connection_timeout=300)
        )
        rabbitmq_channel = rabbitmq_connection.channel()

        # Ensure the target queue exists before the app starts accepting requests.
        # This makes the service more robust.
        rabbitmq_channel.queue_declare(queue='logs', durable=True)
        print("Successfully connected to RabbitMQ.")

    except pika.exceptions.AMQPConnectionError as e:
        print(f"Fatal error connecting to RabbitMQ: {e}")
        # If the message broker is down, the application cannot function.
        raise RuntimeError("Could not connect to RabbitMQ.") from e

    yield  # The application is now running and will process requests here.

    # --- Shutdown Logic ---
    # This block executes when the application is shutting down.
    print("Closing RabbitMQ connection...")
    if rabbitmq_connection and rabbitmq_connection.is_open:
        rabbitmq_connection.close()
    print("Connection closed gracefully.")


app = FastAPI(lifespan=lifespan)


@app.post("/ingest")
async def ingest_log(request: Request):
    """
    Receives a log, validates it, and publishes it to the RabbitMQ queue.
    """
    # A crucial health check. If the broker connection is lost, fail fast.
    if not rabbitmq_channel or not rabbitmq_connection or not rabbitmq_connection.is_open:
        raise HTTPException(
            status_code=503,
            detail="Service Unavailable: Message broker connection is down."
        )

    try:
        log_data = await request.json()

        # Use the single, globally managed channel to publish the message.
        rabbitmq_channel.basic_publish(
            exchange='',
            routing_key='logs',
            body=json.dumps(log_data),
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE,  # Makes messages survive a RabbitMQ restart.
            )
        )

        return {"status": "success"}

    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid request body: Not a valid JSON.")
    except Exception as e:
        # A catch-all for any other unexpected errors during the publishing process.
        print(f"Error publishing to RabbitMQ: {e}")
        raise HTTPException(status_code=500, detail=f"Internal error processing log: {e}")
    