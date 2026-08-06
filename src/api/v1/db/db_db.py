from collections.abc import AsyncGenerator
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from ..config_core import settings

engine = create_async_engine(url=settings.db_url_async, future=True, echo=False)
AsyncSessionLocal = async_sessionmaker(
    bind=engine, expire_on_commit=False, class_=AsyncSession
)


async def get_db() -> AsyncGenerator[AsyncSession, Any]:
    async with AsyncSessionLocal() as db:
        try:
            yield db
        finally:
            await db.close()
