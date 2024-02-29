from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import select, delete

from typing import Type

from core import settings
from core import User, Group


class DatabaseHelper:
    def __init__(self, url: str, echo: bool = False) -> None:
        self.engine = create_async_engine(
            url=url,
            echo=echo,
        )
        self.session_factory = async_sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
        )

    async def create_user(
        self,
        tg_id: int,
        name: str,
        username: str = None,
    ) -> None:
        async with self.session_factory as session:
            session.add(User(tg_id=tg_id, name=name, username=username))
            session.commit()

    async def create_group(
        self,
        tg_id: int,
        name: str,
    ) -> None:
        async with self.session_factory as session:
            session.add(Group(tg_id=tg_id, name=name))
            session.commit()

    async def _get_chat(
        self,
        chat_model: Type[User | Group],
        tg_id: int | None = None,
        code_phrase: str | None = None,
    ) -> User | Group | None:
        if tg_id:
            chat = await self.session_factory().scalar(
                select(chat_model).where(chat_model.tg_id == tg_id)
            )
        elif code_phrase:
            chat = await self.session_factory().scalar(
                select(chat_model).where(chat_model.code_phrase == code_phrase)
            )
        else:
            raise ValueError("One of tg_id or code_phrase must not be None")

        return chat

    async def get_user(
        self,
        tg_id: int = None,
        code_phrase: str = None,
    ) -> User | None:
        return await self._get_chat(User, tg_id, code_phrase)

    async def get_group(
        self,
        tg_id: int = None,
        code_phrase: str = None,
    ) -> Group:
        return await self._get_chat(Group, tg_id, code_phrase)

    async def get_users(self) -> list[User]:
        users = await self.session_factory().scalars(select(User))
        return list(users)

    async def get_groups(self) -> list[Group]:
        groups = await self.session_factory().scalars(select(Group))
        return list(groups)

    async def del_user(self, tg_id: int) -> None:
        await self.session_factory().execute(
            delete(User).where(User.tg_id == tg_id)
        )

    async def del_users(self, tg_ids: list[int]) -> None:
        for tg_id in tg_ids:
            await self.del_user(tg_id)

    async def del_group(self, tg_id: int) -> None:
        await self.session_factory().execute(
            delete(Group).where(Group.tg_id == tg_id)
        )

    async def del_groups(self, tg_ids: list[int]) -> None:
        for tg_id in tg_ids:
            await self.del_group(tg_id)


db_helper = DatabaseHelper(
    settings.db_url,
    settings.db_echo,
)
