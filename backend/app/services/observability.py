"""Structured operational event logging (no commercial payloads)."""
from __future__ import annotations

import logging
from typing import Any
from uuid import UUID

logger = logging.getLogger("cotarco.events")


def log_event(
    event: str,
    *,
    request_id: str | None = None,
    job_id: UUID | str | None = None,
    **fields: Any,
) -> None:
    parts = [f"event={event}"]
    if request_id:
        parts.append(f"request_id={request_id}")
    if job_id is not None:
        parts.append(f"job_id={job_id}")
    for key, value in fields.items():
        if value is None:
            continue
        parts.append(f"{key}={value}")
    logger.info(" ".join(parts))
