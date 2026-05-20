from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


AllowedMethod = Literal["GET", "POST", "PUT", "DELETE"]


class ApiCheckCreate(BaseModel):
    url: str = Field(..., min_length=1, max_length=2048)
    method: AllowedMethod
    headers: dict[str, Any] | None = None
    body: dict[str, Any] | None = None

    @field_validator("method", mode="before")
    @classmethod
    def normalize_method(cls, value: str) -> str:
        if isinstance(value, str):
            return value.upper()
        return value

    @field_validator("headers")
    @classmethod
    def validate_headers(cls, value: dict[str, Any] | None) -> dict[str, str] | None:
        if value is None:
            return None
        if not isinstance(value, dict):
            raise ValueError("Headers must be a JSON object.")
        normalized: dict[str, str] = {}
        for key, header_value in value.items():
            if not isinstance(key, str) or not key.strip():
                raise ValueError("Header names must be non-empty strings.")
            if isinstance(header_value, (dict, list)):
                raise ValueError("Header values must be strings, numbers, booleans, or null.")
            normalized[key] = "" if header_value is None else str(header_value)
        return normalized

    @field_validator("body")
    @classmethod
    def validate_body(cls, value: dict[str, Any] | None) -> dict[str, Any] | None:
        if value is None:
            return None
        if not isinstance(value, dict):
            raise ValueError("Body must be a JSON object.")
        return value


class ApiCheckRead(BaseModel):
    id: int
    url: str
    method: str
    status_code: int | None
    response_time_ms: int | None
    created_at: datetime
    response_summary: str
    success: bool
    error_message: str | None

    model_config = ConfigDict(from_attributes=True)


class ApiCheckRunResponse(BaseModel):
    check: ApiCheckRead
    response: Any | None = None
    response_headers: dict[str, str] = Field(default_factory=dict)
