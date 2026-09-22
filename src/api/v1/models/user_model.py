"""
SQLAlchemy model for the User (Usuário) table.
"""

from typing import Any

from sqlalchemy import TIMESTAMP, Boolean, Column, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship

from .. import config, db

# Columns used for filtering are indexed (i.e., index=True)


class UserModel(db.Base):
    """
    Represents a system user.

    Attributes:
        id: Primary key.
        nome: Unique user name.
        email: Unique email address.
        senha: Hashed password.
        ativo: Whether the user account is active.
        versao_token: Token version for invalidation.
        criado_em: Timestamp when the user was created.
        atualizado_em: Timestamp when the user was last updated.
        id_grupo: Foreign key to the group the user belongs to.
        grupo: Relationship to GroupModel.
    """

    __tablename__ = "usuarios"

    id = Column(type_=Integer, primary_key=True, autoincrement=True)
    nome = Column(type_=String, nullable=False, unique=True, index=True)
    email = Column(type_=String, nullable=False, unique=True, index=True)
    senha = Column(type_=String, nullable=False)
    ativo = Column(type_=Boolean, server_default="true", index=True, nullable=False)
    versao_token = Column(type_=Integer, default=0, server_default="0", nullable=False)
    criado_em = Column(
        type_=TIMESTAMP(timezone=True),
        server_default=func.timezone(config.settings.timezone, func.now()),
        nullable=False,
    )
    atualizado_em = Column(
        type_=TIMESTAMP(timezone=True),
        onupdate=func.timezone(config.settings.timezone, func.now()),
    )
    id_grupo = Column(
        Integer,
        ForeignKey("grupos.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
        unique=False,
        index=False,
    )

    # Relationship to the user's group
    grupo = relationship("GroupModel", back_populates="usuarios")

    @property
    def nome_grupo(self) -> str | None:
        """
        Get the name of the user's group.

        Returns:
            The group name, or None if no group is associated.
        """
        return self.grupo.nome

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the model instance to a dictionary.

        Returns:
            A dictionary containing selected column values.
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
