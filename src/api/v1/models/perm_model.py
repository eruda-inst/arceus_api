from sqlalchemy import TIMESTAMP, Column, Integer, String, func
from sqlalchemy.orm import relationship

from .. import db


class Perm(db.Base):
    __tablename__ = "permissoes"

    id = Column(
        type_=Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
        nullable=False,
        unique=True,
    )
    nome = Column(type_=String, nullable=False, unique=True, index=False)
    codigo = Column(type_=String, nullable=False, unique=True, index=False)
    criado_em = Column(
        type_=TIMESTAMP(timezone=True),
        server_default=func.timezone("America/Bahia", func.now()),
        nullable=False,
        index=False,
        unique=False,
    )
    grupos = relationship(
        argument="Group", secondary="grupos_permissoes", back_populates="permissoes"
    )
