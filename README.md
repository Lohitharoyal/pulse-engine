# PulseEngine - Webhook Processing Service

PulseEngine is a small backend project built to learn how webhook events move through a Python service. It accepts incoming webhook payloads, saves them in PostgreSQL, and hands the work to Celery with Redis in the background. The service uses JSONPath to pull selected values from the payload and updates the record as it moves from received to completed.

## Problem it solves

Many real systems receive instant events from third-party tools, payment gateways, or internal services. Those events need to be stored quickly, processed asynchronously, and monitored. PulseEngine keeps this pattern simple so a junior engineer can explain every part of the flow without extra complexity.

## Features

- FastAPI webhook API with request validation
- PostgreSQL storage with SQLAlchemy models
- Celery background processing with Redis broker
- JSONPath extraction for simple payload values
- Health check and event retrieval endpoints
- Pytest coverage for the main API flows
- Docker Compose for local service startup

## Simple architecture and workflow

External Client
-> FastAPI API
-> PostgreSQL database
-> Celery + Redis worker
-> Background processing
-> PostgreSQL status update

The API writes an event record immediately and returns a `RECEIVED` status. The worker then moves it to `PROCESSING`, extracts the selected values, and marks it as `COMPLETED` or `FAILED`.

## Technologies used

- Python
- FastAPI
- PostgreSQL
- SQLAlchemy
- Celery
- Redis
- JSONPath
- Pytest
- Docker
- Docker Compose

## Project structure

```text
pulse-engine/
|-- app/
|   |-- __init__.py
|   |-- config.py
|   |-- database.py
|   |-- main.py
|   |-- models.py
|   |-- schemas.py
|   |-- tasks.py
|   |-- routes/
|   |   `-- webhooks.py
|   `-- services/
|       `-- processor.py
|-- tests/
|   `-- test_webhooks.py
|-- .env
|-- .env.example
|-- .gitignore
|-- Dockerfile
|-- docker-compose.yml
|-- requirements.txt
`-- README.md
```

## Docker setup

The project is built so it starts with a single command in the repository root.

```powershell
docker compose up --build
```

This starts:
- the FastAPI app on http://localhost:8000
- the PostgreSQL database on localhost:5432
- the Redis broker on localhost:6379
- the Celery worker

## How to run in VS Code

Open the folder in VS Code and use the terminal in the project root. Then run:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

If you want the full stack in containers, use:

```powershell
docker compose up --build
```

## How to test it

Run the unit tests with:

```powershell
pytest
```

You can test the API manually with curl:

```powershell
$body = @{ event_type = "order.created"; payload = @{ order = @{ id = "ORD101"; amount = 1250; customer = @{ name = "Lohitha" } } } } | ConvertTo-Json -Compress
Invoke-RestMethod -Method Post -Uri "http://localhost:8000/webhooks" -ContentType "application/json" -Body $body
```

## API endpoints

### POST /webhooks
Creates a new webhook event and returns the event ID and status.

Example request:

```json
{
  "event_type": "order.created",
  "payload": {
    "order": {
      "id": "ORD101",
      "amount": 1250,
      "customer": {
        "name": "Lohitha"
      }
    }
  }
}
```

Example response:

```json
{
  "event_id": "d5ca0d3d-f7a0-4e9f-909c-c8b0a9238f4c",
  "status": "RECEIVED"
}
```

### GET /webhooks
Returns recent webhook events in descending creation order.

### GET /webhooks/{event_id}
Returns one stored webhook event and its current status.

### GET /health
Returns a simple health response.

## Example webhook request and response

Request:

```json
{
  "event_type": "order.created",
  "payload": {
    "order": {
      "id": "ORD101",
      "amount": 1250,
      "customer": {
        "name": "Lohitha"
      }
    }
  }
}
```

Response:

```json
{
  "event_id": "generated-id",
  "status": "RECEIVED"
}
```

## Celery and Redis explained

Celery is used to move the heavy work out of the API request path. The FastAPI endpoint saves the event and then pushes a background task to Redis. Redis acts as the message broker between the API and the worker. The worker then reads the event, extracts data, and updates the database record. This keeps the API response fast and easy to understand.

## JSONPath processing

JSONPath is used to read values from the event payload without hardcoding nested dictionary access everywhere. In this project, the worker extracts:

- `$.order.id`
- `$.order.amount`
- `$.order.customer.name`

These paths are stored in the `extracted_data` field and can be inspected later in the database or API response.

## Notes for interviews

This project is intentionally small and readable. It is designed to show practical understanding of: request validation, asynchronous task queues, SQLAlchemy models, environment configuration, and a clean local Docker setup.
