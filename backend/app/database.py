from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import settings

DB_POOL_SIZE = 2
DB_MAX_OVERFLOW = 1
# Most connections the engine will ever hand out at once.
DB_POOL_CAPACITY = DB_POOL_SIZE + DB_MAX_OVERFLOW

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_recycle=240,
    pool_size=DB_POOL_SIZE,
    max_overflow=DB_MAX_OVERFLOW,
    pool_timeout=10,
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_database() -> None:
    from app import models

    Base.metadata.create_all(bind=engine)
