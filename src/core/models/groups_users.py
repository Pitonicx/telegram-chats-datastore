from sqlalchemy import (
    Table,
    Column,
    ForeignKey,
    UniqueConstraint,
    Integer,
)

from .base import ChatBase

groups_users_table = Table(
    "groups_users",
    ChatBase.metadata,
    Column("id", Integer, primary_key=True),
    Column("group_id", ForeignKey("groups.id"), nullable=False),
    Column("user_id", ForeignKey("users.id"), nullable=False),
    UniqueConstraint("user_id", "group_id", name="idx_group_user"),
)
