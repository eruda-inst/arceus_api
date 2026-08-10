from sqlalchemy import Column, ForeignKey, Integer, Table

from .. import db

group_perm = Table(
    "grupos_permissoes",
    db.Base.metadata,
    Column("group_id", Integer, ForeignKey("grupos.id")),
    Column("permission_id", Integer, ForeignKey("permissoes.id")),
)
