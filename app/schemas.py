from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class WebhookRequest(BaseModel):
    event_type: str = Field(..., min_length=1)
    payload: dict[str, Any]


class WebhookResponse(BaseModel):
    event_id: str
    status: str


class WebhookEventDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    event_id: str
    event_type: str
    payload: dict[str, Any]
    status: str
    extracted_data: dict[str, Any] | None = None
    error_message: str | None = None
    created_at: datetime
    processed_at: datetime | None = None


class HealthResponse(BaseModel):
    status: str = "ok"