from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import WebhookEvent
from app.schemas import HealthResponse, WebhookEventDetail, WebhookRequest, WebhookResponse
from app.tasks import process_webhook

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health():
    return {"status": "ok"}


@router.post("/webhooks", response_model=WebhookResponse, status_code=status.HTTP_202_ACCEPTED)
def create_webhook(request: WebhookRequest, db: Session = Depends(get_db)):
    if not request.event_type.strip():
        raise HTTPException(status_code=400, detail="event_type cannot be empty.")
    if not isinstance(request.payload, dict):
        raise HTTPException(status_code=400, detail="payload must be a JSON object.")

    event = WebhookEvent(
        event_type=request.event_type.strip(),
        payload=request.payload,
    )
    db.add(event)
    db.commit()
    db.refresh(event)

    try:
        process_webhook.delay(event.id)
    except Exception as exc:
        event.status = "FAILED"
        event.error_message = f"Queue dispatch failed: {str(exc)}"
        db.commit()
        raise HTTPException(
            status_code=503,
            detail="Webhook was saved but could not be queued for processing.",
        ) from exc

    return {"event_id": event.id, "status": event.status.value}


@router.get("/webhooks", response_model=list[WebhookEventDetail])
def list_webhooks(db: Session = Depends(get_db)):
    events = db.query(WebhookEvent).order_by(WebhookEvent.created_at.desc()).limit(20).all()
    return [
        WebhookEventDetail(
            event_id=event.id,
            event_type=event.event_type,
            payload=event.payload,
            status=event.status.value,
            extracted_data=event.extracted_data,
            error_message=event.error_message,
            created_at=event.created_at,
            processed_at=event.processed_at,
        )
        for event in events
    ]


@router.get("/webhooks/{event_id}", response_model=WebhookEventDetail)
def get_webhook(event_id: str, db: Session = Depends(get_db)):
    event = db.query(WebhookEvent).filter(WebhookEvent.id == event_id).first()
    if event is None:
        raise HTTPException(status_code=404, detail="Webhook event not found.")

    return WebhookEventDetail(
        event_id=event.id,
        event_type=event.event_type,
        payload=event.payload,
        status=event.status.value,
        extracted_data=event.extracted_data,
        error_message=event.error_message,
        created_at=event.created_at,
        processed_at=event.processed_at,
    )
