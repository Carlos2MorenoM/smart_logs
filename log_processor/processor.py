import pika
import json

def callback(ch, method, properties, body):
    """
    Executes when a message is received
    """

    log_entry = json.loads(body)

    print(f" New log received and processed {log_entry}")

    # Notify RabbitMQ that the message is processed
    ch.basic_ack(delivery_tag=method.delivery_tag)

    connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
    channel = connection.channel()

    # Queue exists
    channel.queue_declare(queue='logs', durable=True)

    # Consumer for 'logs' queue
    print(" [*] Waiting for logs. Exit using CTRL+C")
    channel.basic_consume(queue='logs', on_message_callback=callback)

    # Start messages receiver loop
    channel.start_consuming()