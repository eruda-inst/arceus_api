from typing import Any

from sqlalchemy import TIMESTAMP, Boolean, Column, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship

from .. import db


class UserModel(db.Base):
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
    versao_token = Column(
        type_=Integer,
        default=0,
        server_default="0",
        nullable=False,
        index=False,
        unique=False,
    )
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

    grupo = relationship("GroupModel", back_populates="usuarios")

    def to_dict(self) -> dict[str, Any]:
        """
        Converte o objeto em um dicionário com tipos Python nativos
        """
        return {
            "id": self.id,
            "nome": self.nome,
            "email": self.email,
            "ativo": self.ativo,
            "id_grupo": self.id_grupo,
            "criado_em": self.criado_em,
            "atualizado_em": self.atualizado_em,
        }
