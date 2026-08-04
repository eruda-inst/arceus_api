from sqlalchemy import TIMESTAMP, Column, Integer, String, func
from sqlalchemy.orm import relationship

from .. import db
from .group_perm_model import group_permission


class Group(db.Base):
    __tablename__ = "grupos"

    id = Column(
        type_=Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
        nullable=False,
        unique=True,
    )
    nome = Column(type_=String, nullable=False, unique=True, index=False)
    criado_em = Column(
        type_=TIMESTAMP(timezone=True),
        server_default=func.timezone("America/Bahia", func.now()),
        nullable=False,
        unique=False,
        index=False,
    )
    usuarios = relationship(argument="User", back_populates="grupo")
    permissoes = relationship(
        argument="Perm", secondary=group_permission, back_populates="grupos"
    )
