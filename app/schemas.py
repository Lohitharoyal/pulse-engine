from pydantic import BaseModel, HttpUrl
from datetime import datetime

class WebhookRuleCreate(BaseModel):
    target_url: HttpUrl
    jsonpath_filter: str

class WebhookRuleResponse(WebhookRuleCreate):
    id: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class IncomingWebhookPayload(BaseModel):
    event: str
    data: dict