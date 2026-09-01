import os

os.environ.setdefault("DATABASE_URL", "sqlite:///./test_pulse.db")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")

from fastapi.testclient import TestClient

from app.database import Base, engine
from app.main import app
from app.routes import webhooks as webhook_routes
from app.tasks import process_webhook


Base.metadata.create_all(bind=engine)
client = TestClient(app)


def reset_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def test_health_endpoint():
    reset_db()
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_webhook_and_retrieve_it():
    reset_db()
    webhook_routes.process_webhook.delay = lambda event_id: None
    payload = {
        "order": {
            "id": "ORD101",
            "amount": 1250,
            "customer": {"name": "Lohitha"},
        }
    }

    response = client.post(
        "/webhooks",
        json={"event_type": "order.created", "payload": payload},
    )

    assert response.status_code == 202
    data = response.json()
    assert data["status"] == "RECEIVED"
    event_id = data["event_id"]

    retrieve = client.get(f"/webhooks/{event_id}")
    assert retrieve.status_code == 200
    event_data = retrieve.json()
    assert event_data["event_id"] == event_id
    assert event_data["status"] == "RECEIVED"
    assert event_data["event_type"] == "order.created"
    assert event_data["payload"]["order"]["id"] == "ORD101"


def test_invalid_request_rejected():
    reset_db()
    response = client.post("/webhooks", json={"payload": {"hello": "world"}})
    assert response.status_code == 422


def test_unknown_event_id_returns_404():
    reset_db()
    response = client.get("/webhooks/unknown-event-id")
    assert response.status_code == 404
    assert response.json()["detail"] == "Webhook event not found."


def test_background_processing_extracts_jsonpath_values():
    reset_db()
    payload = {
        "order": {
            "id": "ORD101",
            "amount": 1250,
            "customer": {"name": "Lohitha"},
        }
    }
    response = client.post(
        "/webhooks",
        json={"event_type": "order.created", "payload": payload},
    )
    event_id = response.json()["event_id"]

    result = process_webhook(event_id)
    assert result["status"] == "COMPLETED"
    assert result["extracted_data"]["$.order.id"] == "ORD101"
    assert result["extracted_data"]["$.order.amount"] == 1250
    assert result["extracted_data"]["$.order.customer.name"] == "Lohitha"

    saved = client.get(f"/webhooks/{event_id}")
    assert saved.status_code == 200
    assert saved.json()["status"] == "COMPLETED"
    assert saved.json()["extracted_data"]["$.order.amount"] == 1250
