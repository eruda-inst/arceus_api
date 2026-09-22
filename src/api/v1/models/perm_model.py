"""
SQLAlchemy model for the Permission (Permissão) table.
"""

from sqlalchemy import TIMESTAMP, Column, Integer, String, func
from sqlalchemy.orm import relationship

from .. import config, db


class PermModel(db.Base):
    """
    Represents a permission that can be assigned to groups.

    Attributes:
        id: Primary key.
        nome: Unique permission name.
        codigo: Unique permission code.
        criado_em: Timestamp when the permission was created.
        grupos: Relationship to GroupModel (many-to-many via grupos_permissoes).
    """

    __tablename__ = "permissoes"

    id = Column(type_=Integer, primary_key=True, autoincrement=True)
    nome = Column(type_=String, nullable=False, unique=True)
    codigo = Column(type_=String, nullable=False, unique=True)
    criado_em = Column(
        type_=TIMESTAMP(timezone=True),
        server_default=func.timezone(config.settings.timezone, func.now()),
        nullable=False,
    )
    # Many-to-many relationship with groups
    grupos = relationship(
        argument="GroupModel",
        secondary="grupos_permissoes",
        back_populates="permissoes",
    )
