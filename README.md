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

