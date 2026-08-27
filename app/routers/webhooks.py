from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models import WebhookRule
from app.schemas import WebhookRuleCreate, WebhookRuleResponse, IncomingWebhookPayload
from app.worker import process_and_dispatch_webhook

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])

@router.post("/rules", response_model=WebhookRuleResponse, status_code=status.HTTP_201_CREATED)
async def create_rule(rule_in: WebhookRuleCreate, db: AsyncSession = Depends(get_db)):
    rule = WebhookRule(target_url=str(rule_in.target_url), jsonpath_filter=rule_in.jsonpath_filter)
    db.add(rule)
    await db.commit()
    await db.refresh(rule)
    return rule

@router.post("/ingest", status_code=status.HTTP_202_ACCEPTED)
async def ingest_webhook(payload: IncomingWebhookPayload, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(WebhookRule))
    rules = result.scalars().all()
    
    dispatched = 0
    for rule in rules:
        process_and_dispatch_webhook.delay(rule.target_url, rule.jsonpath_filter, payload.model_dump())
        dispatched += 1
        
    return {"status": "QUEUED", "rules_matched": dispatched}