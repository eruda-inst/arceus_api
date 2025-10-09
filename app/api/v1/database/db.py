from . import base
from .. import core
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = core.settings.DB_URL

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def criar_tabelas():
    from .. import models

    base.Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
