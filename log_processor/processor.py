import pika
import json
from elasticsearch import Elasticsearch

# Configure and connect Elasticsearch
def connect_to_es():
    try:
        es = Elasticsearch(
            ['http://elasticsearch:9200'],
            verify_certs=False,
        )
        return es
    except Exception as e:
        print(f"Error connecting to Elasticsearch: {e}")
        return None

# Define processor function
def callback(ch, method, properties, body):
    try:
        log_entry = json.loads(body)
        print(f"✅ New log received and processed: {log_entry}")

        es_client.index(index="logs", document=log_entry)
        print("📦 Log stored on Elasticsearch")

        # Notify RabbitMQ message was processed
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        print(f"❌ Error processing log message: {e}")

if __name__ == '__main__':
    # Connect Elasticsearch
    es_client = connect_to_es()
    if es_client is None:
        exit(1)

    # Connect RabbitMQ
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
    channel = connection.channel()

    # Keeping sure queue exists
    channel.queue_declare(queue='logs', durable=True)

    # Configure the consumer
    channel.basic_consume(queue='logs', on_message_callback=callback, auto_ack=False)

    print(" [*] Waiting for logs. Exit using CTRL+C")
    # Consume messages
    channel.start_consuming()