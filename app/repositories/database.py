from __future__ import annotations

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATABASE_URL: str = os.getenv(
    "DATABASE_URL",
    "postgresql://fintech:fintech@db:5432/fintech",
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,   # detect stale connections
    echo=False,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    """Shared declarative base for all ORM models."""
    pass


def get_session():
    """FastAPI / general dependency: yields a session and closes it after use."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()