from sqlalchemy import TIMESTAMP, Column, Integer, String, func
from sqlalchemy.orm import relationship

from .. import db
from .group_perm_model import group_perm

# Default value for unique: False
# Default value for index: False
# Default value for nullable: True

# Primary keys have: nullable=False
# Primary keys have: unique=True
# Primary keys index: index=True

# Columns used for filtering are indexed (i.e., index=True)


class GroupModel(db.Base):
    __tablename__ = "grupos"

    id = Column(type_=Integer, primary_key=True, autoincrement=True)
    nome = Column(type_=String, nullable=False, unique=True)
    criado_em = Column(
        type_=TIMESTAMP(timezone=True),
        server_default=func.timezone("America/Bahia", func.now()),
        nullable=False,
    )
    usuarios = relationship(argument="UserModel", back_populates="grupo")
    permissoes = relationship(
        argument="PermModel", secondary=group_perm, back_populates="grupos"
    )
