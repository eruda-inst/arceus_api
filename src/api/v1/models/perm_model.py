from sqlalchemy import TIMESTAMP, Column, Integer, String, func
from sqlalchemy.orm import relationship

from .. import db

# Default value for unique: False
# Default value for index: False
# Default value for nullable: True

# Primary keys have: nullable=False
# Primary keys have: unique=True
# Primary keys index: index=True


class PermModel(db.Base):
    __tablename__ = "permissoes"

    id = Column(type_=Integer, primary_key=True, autoincrement=True)
    nome = Column(type_=String, nullable=False, unique=True)
    codigo = Column(type_=String, nullable=False, unique=True)
    criado_em = Column(
        type_=TIMESTAMP(timezone=True),
        server_default=func.timezone("America/Bahia", func.now()),
        nullable=False,
    )
    grupos = relationship(
        argument="GroupModel",
        secondary="grupos_permissoes",
        back_populates="permissoes",
    )
