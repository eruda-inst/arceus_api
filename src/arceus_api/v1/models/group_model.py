"""
SQLAlchemy model for the Group (Grupo) table.
"""

from sqlalchemy import TIMESTAMP, Column, Integer, String, func
from sqlalchemy.orm import relationship

from .. import config, db
from .group_perm_model import group_perm

# Columns used for filtering are indexed (i.e., index=True)


class GroupModel(db.Base):
    """
    Represents a group of users.

    Attributes:
        id: Primary key.
        nome: Unique group name.
        criado_em: Timestamp when the group was created.
        usuarios: Relationship to UserModel (one-to-many).
        permissoes: Relationship to PermModel (many-to-many via group_perm).
    """

    __tablename__ = "grupos"

    id = Column(type_=Integer, primary_key=True, autoincrement=True)
    nome = Column(type_=String, nullable=False, unique=True)
    criado_em = Column(
        type_=TIMESTAMP(timezone=True),
        server_default=func.timezone(config.settings.timezone, func.now()),
        nullable=False,
    )
    # Relationship to users belonging to this group
    usuarios = relationship(argument="UserModel", back_populates="grupo")
    # Many-to-many relationship with permissions
    permissoes = relationship(
        argument="PermModel", secondary=group_perm, back_populates="grupos"
    )
