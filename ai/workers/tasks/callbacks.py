import json
import os
import time
from functools import lru_cache
from http.client import HTTPConnection
from uuid import UUID, uuid4

from sqlalchemy import create_engine, select
from sqlalchemy.engine import make_url

from ai.contracts.hmac import sign
from ai.workers.celery_app import celery_app
from collections.abc import Callable
from sqlalchemy.orm import Session

from ai.persistence.models import OutboxCallback


def add_pending_callback(
    session: Session,
    *,
    target_path: str,
    body: dict,
    sequence: int,
) -> dict:
    row = OutboxCallback(
        outbox_id=uuid4(),
        target_path=target_path,
        body=body,
        sequence=sequence,
        state="pending",
    )
    session.add(row)

    return {
        "outbox_id": row.outbox_id,
        "target_path": row.target_path,
        "sequence": row.sequence,
        "state": row.state,
    }
def apply_callback_response(
    row: OutboxCallback,
    *,
    status_code: int,
    response_body: object,
) -> None:
    if row.state != "pending" or not 200 <= status_code < 300:
        return

    if not isinstance(response_body, dict):
        return

    receipt = response_body.get("data")
    if not isinstance(receipt, dict):
        return

    if receipt.get("accepted") is True and isinstance(receipt.get("duplicate"), bool):
        row.state = "delivered"

def deliver_pending_callback(
    row: OutboxCallback,
    *,
    post_callback: Callable[[str, dict], tuple[int, object]],
) -> None:
    if row.state != "pending":
        return

    status_code, response_body = post_callback(row.target_path, row.body)
    apply_callback_response(
        row,
        status_code=status_code,
        response_body=response_body,
    )

@lru_cache(maxsize=1)
def _database_engine():
    url = make_url(os.environ["AI_DATABASE_URL"])
    if url.drivername == "postgresql":
        url = url.set(drivername="postgresql+psycopg")
    return create_engine(url)


def _post_to_backend(path: str, body: dict) -> tuple[int, object]:
    raw = json.dumps(body, separators=(",", ":")).encode("utf-8")
    timestamp = str(int(time.time()))
    signature = sign(os.environ["AI_TO_NEST_HMAC_SECRET"], timestamp, "POST", path, raw)
    headers = {
        "Content-Type": "application/json",
        "X-Shawaf-Service": "inference",
        "X-Shawaf-Timestamp": timestamp,
        "X-Shawaf-Signature": f"v1={signature}",
        "X-Request-Id": str(uuid4()),
    }
    connection = HTTPConnection("backend", 4000, timeout=10)
    try:
        connection.request("POST", path, body=raw, headers=headers)
        response = connection.getresponse()
        if 200 <= response.status < 300:
            return response.status, json.load(response)
        return response.status, None
    finally:
        connection.close()


@celery_app.task(name="callbacks.deliver")
def deliver(outbox_id: str) -> None:
    with Session(_database_engine()) as session, session.begin():
        row = session.scalars(select(OutboxCallback).where(OutboxCallback.outbox_id == UUID(outbox_id)).with_for_update()).one()
        deliver_pending_callback(row, post_callback=_post_to_backend)
