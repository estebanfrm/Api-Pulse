from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ApiCheck(Base):
    __tablename__ = "api_checks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    url: Mapped[str] = mapped_column(Text, nullable=False)
    method: Mapped[str] = mapped_column(Text, nullable=False)
    status_code: Mapped[int | None] = mapped_column(Integer, nullable=True)
    response_time_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    response_summary: Mapped[str] = mapped_column(Text, nullable=False, default="")
    success: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
