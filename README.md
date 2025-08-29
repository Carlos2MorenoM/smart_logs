# SmartLogs: A Log Management Platform

### Description

SmartLogs is a real-time log management platform designed to collect, process, store, and visualize log data from applications. The architecture is based on microservices, making it a flexible and highly scalable solution for projects of any size.

### Application Architecture

The application follows a decoupled microservices architecture where each component handles a specific responsibility. Communication between services is managed via a message queue.



### Technologies Used

* **Python:** The core language for the business logic in the ingestion and processing services.
* **FastAPI:** A modern, high-performance web framework for the log ingestion API.
* **RabbitMQ:** A message broker used to manage the log queue, ensuring reliable communication.
* **Elasticsearch:** A distributed search and analytics engine optimized for storing and querying large volumes of log data.
* **Kibana:** The data visualization interface for Elasticsearch, used to create dashboards and explore logs.
* **Docker & Docker Compose:** Used to orchestrate and manage all application services in a local development environment.

### Getting Started

To get the application up and running, you only need to have [Docker and Docker Compose](https://docs.docker.com/compose/install/) installed.

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/smartlogs.git
    cd smartlogs
    ```
2.  **Run the services:**
    ```bash
    docker-compose up --build -d
    ```
    This command will build the images, start all services, and run them in the background.

### Usage

#### 1. Send a Log

Use the following `curl` command to send a test log to the ingestion API.

```bash
curl -X POST http://localhost:8000/ingest -H "Content-Type: application/json" -d '{"level": "info", "message": "Hello from SmartLogs!", "timestamp": "2025-08-30T10:00:00Z"}'
 ```

#### 2. View Logs in Kibana
Once the logs are processed, you can view them in Kibana.

Open your browser and go to `http://localhost:5601`.

In the Kibana application, go to **"Stack Management"** > **"Data Views"** and create a new data view named `logs`, selecting the `timestamp` field as the time field.

Go to the "Discover" tab and select the `logs` data view to see your records.



### Future Plans
**Machine Learning Analysis:** Integrate machine learning models for anomaly detection and pattern analysis in the logs.

**Custom User Interface:** Develop a custom graphical user interface using a web framework.

**Cloud Deployment & Scalability:** Migrate the architecture to a production environment using managed services like Elastic Cloud or AWS OpenSearch Service, and implement a container orchestration platform like Kubernetes to manage scalability and high availability.

### Author
Carlos Moreno and Gemini :)
