from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from jsonpath_ng import parse

JSONPATH_FIELDS = [
    "$.order.id",
    "$.order.amount",
    "$.order.customer.name",
]


def extract_selected_values(payload: dict[str, Any]) -> dict[str, Any]:
    extracted: dict[str, Any] = {}
    for path in JSONPATH_FIELDS:
        matches = parse(path).find(payload)
        if not matches:
            continue
        extracted[path] = matches[0].value
    return extracted


def mark_complete(event, db_session) -> None:
    event.status = "COMPLETED"
    event.processed_at = datetime.now(timezone.utc)
    db_session.commit()


def mark_failed(event, db_session, error_message: str) -> None:
    event.status = "FAILED"
    event.error_message = error_message
    event.processed_at = datetime.now(timezone.utc)
    db_session.commit()
