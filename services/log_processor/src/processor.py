# services/log_processor/src/processor.py

import pika
import json
import time
import requests
from elasticsearch import Elasticsearch

# --- Configuration ---
ANOMALY_DETECTOR_URL = "http://anomaly_detector:8001/predict"


def get_anomaly_prediction(log_message: str) -> bool:
    """
    Calls the anomaly_detector microservice to get a prediction.
    """
    try:
        response = requests.post(ANOMALY_DETECTOR_URL, json={"message": log_message}, timeout=2)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        return response.json().get("is_anomaly", False)
    except requests.exceptions.RequestException as e:
        print(f"🚨 Could not connect to anomaly detector: {e}")
        # Failsafe: if the model service is down, we don't classify as an anomaly.
        return False


def process_log(log_data: dict, es_client: Elasticsearch):
    """
    Processes a single log: calls the ML service and stores result in Elasticsearch.
    """
    try:
        log_message = log_data.get("message", "")

        # Call the dedicated microservice for prediction
        is_anomaly = get_anomaly_prediction(log_message)

        # Enrich the log data with the prediction
        log_data['is_anomaly'] = is_anomaly
        if is_anomaly:
            log_data['tags'] = ['anomaly']

        print(f"-> Processing log {log_data.get('log_id', 'N/A')}. Anomaly: {is_anomaly}")

        # Store the enriched log in Elasticsearch
        es_client.index(index="smartlogs", document=log_data)

    except Exception as e:
        print(f"🚨 Error processing log: {e}")


def main():
    es = Elasticsearch("http://elasticsearch:9200")
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
    channel = connection.channel()
    channel.queue_declare(queue='logs', durable=True)

    def callback(ch, method, properties, body):
        log_payload = json.loads(body)
        process_log(log_payload, es)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(queue='logs', on_message_callback=callback)
    print(' [*] Waiting for logs. To exit press CTRL+C')
    channel.start_consuming()


if __name__ == '__main__':
    time.sleep(15)
    main()
