# SmartLogs: A Log Management Platform

### Description

SmartLogs is a real-time log management platform designed to collect, process, store, and visualize log data from applications. The architecture is based on microservices, making it a flexible and highly scalable solution for projects of any size.

### Application Architecture

The application follows a decoupled microservices architecture where each component handles a specific responsibility. Communication between services is managed via a message queue.

The data flow is as follows:

`Ingestion Script` → `Log Ingestor (API)` → `RabbitMQ (Queue)` → `Log Processor` → `Elasticsearch` → `Kibana`

* **Log Ingestor:** A FastAPI-based API that receives logs via HTTP requests and publishes them to the message queue.
* **RabbitMQ:** Acts as a message broker. It receives logs from the ingestor and holds them in a queue until they are consumed, decoupling the ingestion from the processing.
* **Log Processor:** A service that consumes logs from the queue. It enriches the data, formats it, and runs an **anomaly detection model** before storing the final result in Elasticsearch.
* **Elasticsearch:** A distributed search and analytics engine where all processed logs are stored.
* **Kibana:** The visualization layer, used to explore logs and build dashboards on top of the data in Elasticsearch.


### Getting Started

To get the application up and running, you only need to have [Docker and Docker Compose](https://docs.docker.com/compose/install/) installed.

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Carlos2MorenoM/smart_logs.git
    cd smart_logs
    ```
2.  **Run the core services:**
    This command will build the images and start all the core components (API, processor, RabbitMQ, Elasticsearch, Kibana) in the background.
    ```bash
    docker-compose up --build -d
    ```

### Usage
#### 1. Ingest Sample Data
To populate Elasticsearch with the provided sample logs (`Linux_2k.log`), run the ingestion script using its dedicated profile. This script will read the log file and send each line to the ingestion API.

```bash
docker-compose --profile setup up --build ingestion_script
#### 1. Send a Log
```

#### 2. View Logs in Kibana
Once the logs are processed, you can view them in Kibana.

Open your browser and go to `http://localhost:5601`.

In the Kibana application, go to **"Stack Management"** > **"Data Views"** and create a new data view named `logs`, selecting the `timestamp` field as the time field.

Go to the "Discover" tab and select the `logs` data view to see your records.

#### 3. Send a Single Log (Optional)
You can also send a single test  log directly to the ingestion API using `curl`
```bash
curl -X POST http://localhost:8000/ingest -H "Content-Type: application/json" -d '{"message": "This is a test log message from curl"}'
```

### Future Plans
**Machine Learning Analysis:** Integrate machine learning models for anomaly detection and pattern analysis in the logs.

**From Script to Service:** Evolve the ingest_logs.py script into a dedicated microservice (ingestion-service) that can listen to various sources, such as a Kafka topic or logs shipped by Filebeat.

**Real Model Training:** Replace the previous rule-based logic in core/model.py with a genuine, trained anomaly detection model (e.g., using Isolation Forest or an LSTM autoencoder). This will involve creating a new training-pipeline component.

**CI/CD Implementation:** Leverage the monorepo structure and Docker Compose to build a CI/CD pipeline (e.g., using GitHub Actions) that automatically tests and deploys changes to the services.

**Observability:** Introduce centralized logging, metrics (Prometheus), and tracing (Jaeger) for the microservices to monitor their health and performance in production.

**Custom User Interface:** Develop a custom graphical user interface using a modern web framework to provide a more tailored user experience.

**Cloud Deployment & Scalability:** Migrate the architecture to a production environment using managed services (e.g., Elastic Cloud, AWS OpenSearch) and implement a container orchestrator like Kubernetes to manage scalability and high availability.

### Author
Carlos Moreno and Gemini :)
