from fastapi import APIRouter, Depends, Query
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import ApiCheck
from app.schemas import ApiCheckCreate, ApiCheckRead, ApiCheckRunResponse
from app.services.api_client import ApiClientResult, execute_api_request
from app.services.security import SecurityValidationError, validate_public_url

router = APIRouter()


@router.post("", response_model=ApiCheckRunResponse)
def create_check(payload: ApiCheckCreate, db: Session = Depends(get_db)) -> ApiCheckRunResponse:
    try:
        safe_url = validate_public_url(payload.url)
        result = execute_api_request(
            url=safe_url,
            method=payload.method,
            headers=payload.headers,
            body=payload.body,
        )
    except SecurityValidationError as exc:
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
        url=payload.url,
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

    return ApiCheckRunResponse(
        check=check,
        response=result.response_body,
        response_headers=result.response_headers,
    )


@router.get("", response_model=list[ApiCheckRead])
def list_checks(
    limit: int = Query(default=50, ge=1, le=100),
    db: Session = Depends(get_db),
) -> list[ApiCheck]:
    return (
        db.query(ApiCheck)
        .order_by(desc(ApiCheck.created_at))
        .limit(limit)
        .all()
    )
