from dataclasses import replace
from datetime import datetime, timedelta, timezone
import json

import httpx
from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy import and_, delete, desc, or_, select
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import ApiCheck
from app.schemas import ApiCheckCreate, ApiCheckRead, ApiCheckRunResponse
from app.services.api_client import ApiClientResult, execute_api_request
from app.services.demo import BLOCKED_URL, DEMO_URLS, safe_summary, scenario_response, validate_demo_url
from app.services.limits import demo_limiter
from app.services.security import SecurityValidationError, redact_url_credentials, validate_public_url

router = APIRouter()


# The "/" alias keeps /api/checks/ working without a slash redirect, which would be
# built from the unencrypted origin scheme behind the proxy.
@router.post("", response_model=ApiCheckRunResponse)
@router.post("/", response_model=ApiCheckRunResponse, include_in_schema=False)
def create_check(payload: ApiCheckCreate, request: Request, db: Session = Depends(get_db)) -> ApiCheckRunResponse:
    if settings.public_demo:
        client_key = request.client.host if request.client else "unknown"
        with demo_limiter.admit(client_key):
            return _run_check(payload, db)
    return _run_check(payload, db)


def _run_check(payload: ApiCheckCreate, db: Session) -> ApiCheckRunResponse:
    stored_url = redact_url_credentials(payload.url)
    try:
        if settings.public_demo:
            safe_url = validate_demo_url(payload.url)
            stored_url = safe_url
        else:
            safe_url = validate_public_url(payload.url)
        result = execute_api_request(
            url=safe_url,
            method=payload.method,
            headers=payload.headers,
            body=payload.body,
            **(
                {"transport": httpx.MockTransport(scenario_response), "timeout_seconds": settings.demo_timeout_seconds}
                if settings.public_demo
                else {}
            ),
        )
        if settings.public_demo:
            response_size = len(json.dumps(result.response_body, ensure_ascii=False).encode("utf-8"))
            if response_size > settings.demo_max_response_bytes:
                result = ApiClientResult(
                    success=False,
                    status_code=None,
                    response_time_ms=result.response_time_ms,
                    response_summary="",
                    response_body=None,
                    response_headers={},
                    error_message="Demo response exceeded the size limit.",
                )
            result = replace(
                result,
                response_summary=safe_summary(stored_url, payload.method, result.status_code),
            )
    except SecurityValidationError as exc:
        if settings.public_demo:
            stored_url = BLOCKED_URL
        result = ApiClientResult(
            success=False,
            status_code=None,
            response_time_ms=None,
            response_summary="",
            response_body=None,
            response_headers={},
            error_message=str(exc),
        )

    check = ApiCheck(
        url=stored_url,
        method=payload.method,
        status_code=result.status_code,
        response_time_ms=result.response_time_ms,
        response_summary=result.response_summary,
        success=result.success,
        error_message=result.error_message,
    )
    db.add(check)
    db.commit()
    db.refresh(check)
    if settings.public_demo:
        _prune_history(db)

    return ApiCheckRunResponse(
        check=check,
        response=result.response_body,
        response_headers=result.response_headers,
    )


@router.get("", response_model=list[ApiCheckRead])
@router.get("/", response_model=list[ApiCheckRead], include_in_schema=False)
def list_checks(
    limit: int = Query(default=50, ge=1, le=100),
    db: Session = Depends(get_db),
) -> list[ApiCheck]:
    if settings.public_demo:
        _prune_history(db)
    return (
        db.query(ApiCheck)
        .order_by(desc(ApiCheck.created_at), desc(ApiCheck.id))
        .limit(limit)
        .all()
    )


def _prune_history(db: Session) -> None:
    cutoff = datetime.now(timezone.utc) - timedelta(hours=settings.history_retention_hours)
    db.execute(delete(ApiCheck).where(ApiCheck.created_at < cutoff).execution_options(synchronize_session=False))
    safe_record = or_(
        and_(ApiCheck.url.in_(DEMO_URLS), ApiCheck.response_summary.like("Demo %")),
        and_(
            ApiCheck.url == BLOCKED_URL,
            ApiCheck.error_message == "Blocked target. Choose one of the demo scenarios.",
        ),
    )
    db.execute(delete(ApiCheck).where(~safe_record).execution_options(synchronize_session=False))
    excess_ids = (
        select(ApiCheck.id)
        .order_by(desc(ApiCheck.created_at), desc(ApiCheck.id))
        .offset(settings.history_max_records)
    )
    db.execute(delete(ApiCheck).where(ApiCheck.id.in_(excess_ids)).execution_options(synchronize_session=False))
    db.commit()
