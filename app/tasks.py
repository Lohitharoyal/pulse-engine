from __future__ import annotations

from datetime import datetime, timezone

from celery import Celery
from sqlalchemy.orm import Session

from app.config import settings
from app.database import SessionLocal
from app.models import WebhookEvent
from app.services.processor import extract_selected_values


celery_app = Celery(
    "pulse_engine",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
)


@celery_app.task(name="app.tasks.process_webhook")
def process_webhook(event_id: str):
    db: Session = SessionLocal()
    try:
        event = db.query(WebhookEvent).filter(WebhookEvent.id == event_id).first()
        if event is None:
            raise ValueError(f"Webhook event {event_id} was not found.")

        event.status = "PROCESSING"
        db.commit()

        extracted_data = extract_selected_values(event.payload)
        event.extracted_data = extracted_data
        event.status = "COMPLETED"
        event.processed_at = datetime.now(timezone.utc)
        event.error_message = None
        db.commit()
        return {
            "status": "COMPLETED",
            "event_id": event_id,
            "extracted_data": extracted_data,
        }
    except Exception as exc:
        event = db.query(WebhookEvent).filter(WebhookEvent.id == event_id).first()
        if event is not None:
            event.status = "FAILED"
            event.error_message = str(exc)
            event.processed_at = datetime.now(timezone.utc)
            db.commit()
        raise
    finally:
        db.close()
