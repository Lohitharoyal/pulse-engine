from celery import Celery
import httpx
import jsonpath_ng
from app.config import settings

celery_app = Celery("pulse_worker", broker=settings.REDIS_URL, backend=settings.REDIS_URL)

@celery_app.task(bind=True, max_retries=3, default_retry_delay=5)
def process_and_dispatch_webhook(self, target_url: str, jsonpath_filter: str, payload: dict):
    try:
        jsonpath_expr = jsonpath_ng.parse(jsonpath_filter)
        matches = [match.value for match in jsonpath_expr.find(payload)]
        if not matches:
            return {"status": "SKIPPED", "reason": "Payload did not match filter"}
    except Exception as err:
        return {"status": "FAILED", "reason": f"Filter error: {str(err)}"}

    try:
        response = httpx.post(target_url, json=payload, timeout=5.0)
        response.raise_for_status()
        return {"status": "SUCCESS", "status_code": response.status_code}
    except httpx.HTTPError as exc:
        retry_backoff = 5 * (2 ** self.request.retries)
        raise self.retry(exc=exc, countdown=retry_backoff)