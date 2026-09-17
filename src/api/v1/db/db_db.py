"""
Database engine, session factory, and dependency for FastAPI.
"""

from collections.abc import AsyncGenerator
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from ..config import settings

# Create the asynchronous database engine
engine = create_async_engine(
    url=settings.db_url_async,
    future=True,
    echo=False,
    pool_pre_ping=True,  # Verify connections before using them
    pool_recycle=3600,  # Recycle connections after 1 hour
)

# Session factory for creating async sessions
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
)


async def get_db() -> AsyncGenerator[AsyncSession, Any]:
    """
    FastAPI dependency that provides an async database session.

    Yields:
        AsyncSession: A database session that is automatically closed after use.
    """
    async with AsyncSessionLocal() as db:
        try:
            yield db
        finally:
            await db.close()
