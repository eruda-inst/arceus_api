from . import base
from .. import core
from typing import Generator, Any
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = core.settings.DB_URL

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def criar_tabelas() -> None:
    """Cria todas as tabelas no banco de dados com base nos modelos definidos."""
    from .. import models

    base.Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Any, Any, Any]:
    """
    Fornece uma sessão de banco de dados para uma requisição.

    Esta é uma função geradora que cria uma nova sessão para cada requisição,
    a disponibiliza e garante que seja fechada no final, mesmo em caso de erro.

    Yields:
        Session: A sessão do banco de dados.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
