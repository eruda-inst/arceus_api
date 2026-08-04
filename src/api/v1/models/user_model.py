from sqlalchemy import TIMESTAMP, Boolean, Column, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship

from .. import db


class User(db.Base):
    __tablename__ = "usuarios"

    id = Column(
        type_=Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
        nullable=False,
        unique=True,
    )
    nome = Column(type_=String, nullable=False, unique=True, index=True)
    email = Column(type_=String, nullable=False, unique=True, index=True)
    senha = Column(type_=String, nullable=False, unique=True, index=False)
    ativo = Column(type_=Boolean, default=True, nullable=True, unique=False, index=True)
    criado_em = Column(
        type_=TIMESTAMP(timezone=True),
        server_default=func.timezone("America/Bahia", func.now()),
        nullable=False,
        unique=False,
        index=False,
    )
    atualizado_em = Column(
        type_=TIMESTAMP(timezone=True),
        onupdate=func.timezone("America/Bahia", func.now()),
        nullable=True,
        unique=False,
        index=False,
    )
    id_grupo = Column(
        Integer,
        ForeignKey("grupos.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
        unique=False,
        index=False,
    )

    grupo = relationship("Group", back_populates="usuarios")
