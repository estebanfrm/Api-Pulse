from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


AllowedMethod = Literal["GET", "POST", "PUT", "DELETE"]

HEADER_TEXT_ERROR = (
    "Header names and values must use printable ASCII characters without line breaks."
)


def _is_unsafe_header_text(text: str) -> bool:
    """Reject control characters and non-ASCII text before they reach the HTTP client.

    CR, LF and NUL are the characters used for header injection, and non-ASCII text
    fails inside httpx with an opaque error instead of a usable message.
    """
    return any(character != "\t" and (ord(character) < 32 or ord(character) > 126) for character in text)


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
            text = "" if header_value is None else str(header_value)
            if _is_unsafe_header_text(key) or _is_unsafe_header_text(text):
                raise ValueError(HEADER_TEXT_ERROR)
            normalized[key] = text
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
