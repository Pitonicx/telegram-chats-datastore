from sqlalchemy.orm import DeclarativeBase, declared_attr, Mapped, mapped_column


class Base(DeclarativeBase):
    ...


class ChatBase(Base):
    # when the parameter is True, this table will not be created
    __abstract__ = True

    # creating a table name based on its class name
    @declared_attr
    def __tablename__(cls) -> str:
        return f"{cls.__name__.lower()}s"

    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)  # id of row
    tg_id: Mapped[int] = mapped_column(unique=True)  # telegram id of chat
    name: Mapped[str]  # name of chat
    activity: Mapped[bool] = mapped_column(default=True)  # will the chat receive a message
    code_phrase: Mapped[str | None]  # needed for bot functional

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(id={self.id}, name={self.name})"

    def __repr__(self) -> str:
        return str(self)
