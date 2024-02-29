from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, relationship

from .base import ChatBase
from .groups_users import groups_users_table

if TYPE_CHECKING:
    from .user import User


class Group(ChatBase):
    members: Mapped[list["User"] | None] = relationship(
        back_populates="groups",
        secondary=groups_users_table,
    )
