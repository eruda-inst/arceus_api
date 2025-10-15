from . import base
from .. import core
from typing import AsyncGenerator, Any
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

DATABASE_URL = core.settings.DB_URL.replace("postgresql://", "postgresql+asyncpg://")

engine = create_async_engine(DATABASE_URL, future=True, echo=False)
AsyncSessionLocal = async_sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)


async def criar_tabelas() -> None:
    """Cria todas as tabelas no banco de dados com base nos modelos definidos."""
    from .. import models

    async with engine.begin() as conn:
        await conn.run_sync(base.Base.metadata.create_all)


async def get_db() -> AsyncGenerator[AsyncSession, Any]:
    """
    Fornece uma sessão de banco de dados assíncrona para uma requisição.

    Esta é uma função geradora que cria uma nova sessão para cada requisição,
    a disponibiliza e garante que seja fechada no final, mesmo em caso de erro.

    Yields:
        AsyncSession: A sessão do banco de dados.
    """
    async with AsyncSessionLocal() as db:
        try:
            yield db
        finally:
            await db.close()
