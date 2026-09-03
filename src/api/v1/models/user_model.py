from typing import Any

from sqlalchemy import TIMESTAMP, Boolean, Column, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship

from .. import db

# Valor padrão para unique: False
# Valor padrão para index: False
# Valor padrão para nullable: True

# Primary keys possuem: nullable=False
# Primary keys possuem: unique=True
# Primary keys index: index=True


class UserModel(db.Base):
    __tablename__ = "usuarios"

    # Colunas utilizadas em filtro são indexadas
    id = Column(type_=Integer, primary_key=True, autoincrement=True)
    nome = Column(type_=String, nullable=False, unique=True, index=True)
    email = Column(type_=String, nullable=False, unique=True, index=True)
    senha = Column(type_=String, nullable=False)
    ativo = Column(type_=Boolean, server_default="true", index=True, nullable=False)
    versao_token = Column(type_=Integer, default=0, server_default="0", nullable=False)
    criado_em = Column(
        type_=TIMESTAMP(timezone=True),
        server_default=func.timezone("America/Bahia", func.now()),
        nullable=False,
    )
    atualizado_em = Column(
        type_=TIMESTAMP(timezone=True),
        onupdate=func.timezone("America/Bahia", func.now()),
    )
    id_grupo = Column(
        Integer,
        ForeignKey("grupos.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
        unique=False,
        index=False,
    )

    grupo = relationship("GroupModel", back_populates="usuarios")

    @property
    def nome_grupo(self) -> str | None:
        """
        Retorna o nome do grupo associado
        """
        return self.grupo.nome

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
