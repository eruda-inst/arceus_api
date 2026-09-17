"""
Association table for the many-to-many relationship between groups and permissions.
"""

from sqlalchemy import Column, ForeignKey, Integer, Table

from .. import db

# Association table linking groups and permissions
group_perm = Table(
    "grupos_permissoes",
    db.Base.metadata,
    # Foreign key to the groups table
    Column("group_id", Integer, ForeignKey("grupos.id")),
    # Foreign key to the permissions table
    Column("permission_id", Integer, ForeignKey("permissoes.id")),
)
