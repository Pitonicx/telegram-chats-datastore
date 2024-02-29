from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, relationship

from .base import ChatBase
from .groups_users import groups_users_table

if TYPE_CHECKING:
    from .group import Group


class User(ChatBase):
    username: Mapped[str | None]
    groups: Mapped[list["Group"] | None] = relationship(
        back_populates="members",
        secondary=groups_users_table,
    )
