from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)
from sqlalchemy.orm import selectinload
from sqlalchemy import select, delete

from core import settings
from core import User, Group

from typing import Type


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

    async def _create_chat(
        self,
        session: AsyncSession,
        chat_type: Type[User | Group],
        tg_id: int,
        name: str,
    ) -> User | Group | None:
        if await self._get_chat(session, chat_type, tg_id) is None:
            chat = chat_type(tg_id=tg_id, name=name)
            session.add(chat)
            await session.commit()
            return chat
        else:
            print(f"Was attempted to create existing chat - id {tg_id}")

    @staticmethod
    async def _get_chat(
        session: AsyncSession,
        chat_type: Type[User | Group],
        tg_id: int = None,
        code_phrase: str = None,
    ) -> User | Group | None:
        if not tg_id and not code_phrase:
            raise ValueError("One of tg_id or code_phrase must not be None")

        attr = getattr(chat_type, "groups" if chat_type is User else "members")
        chat = select(chat_type).options(selectinload(attr))

        if tg_id:
            chat = chat.where(chat_type.tg_id == tg_id)
        elif code_phrase:
            chat = chat.where(chat_type.code_phrase == code_phrase)

        return await session.scalar(chat)

    async def _update_chat(
        self,
        session: AsyncSession,
        chat_type: Type[User | Group],
        tg_id: int,
        **kwargs: dict,
    ) -> User | Group:
        chat = await self._get_chat(session, chat_type, tg_id)
        for key, value in kwargs.items():
            setattr(chat, key, value)
        await session.commit()
        return chat

    async def create_user(
        self,
        tg_id: int,
        name: str,
    ) -> User | None:
        async with self.session_factory() as session:
            return await self._create_chat(session, User, tg_id, name)

    async def create_group(
        self,
        tg_id: int,
        name: str,
    ) -> Group | None:
        async with self.session_factory() as session:
            return await self._create_chat(session, Group, tg_id, name)

    async def get_user(
        self,
        tg_id: int = None,
        code_phrase: str = None,
    ) -> User | None:
        async with self.session_factory() as session:
            return await self._get_chat(session, User, tg_id, code_phrase)

    async def get_group(
        self,
        tg_id: int = None,
        code_phrase: str = None,
    ) -> Group | None:
        async with self.session_factory() as session:
            return await self._get_chat(session, Group, tg_id, code_phrase)

    async def get_users(self) -> list[User]:
        users = await self.session_factory().scalars(select(User))
        return list(users)

    async def get_groups(self) -> list[Group]:
        groups = await self.session_factory().scalars(select(Group))
        return list(groups)

    async def update_user(
        self,
        tg_id: int,
        **kwargs,
    ) -> User:
        async with self.session_factory() as session:
            return await self._update_chat(session, User, tg_id, **kwargs)

    async def update_group(
        self,
        tg_id: int,
        **kwargs,
    ) -> Group:
        async with self.session_factory() as session:
            return await self._update_chat(session, Group, tg_id, **kwargs)

    async def add_member(
        self,
        member_id: int,
        group_id: int,
    ) -> None:
        async with self.session_factory() as session:
            member = await self._get_chat(session, User, member_id)
            group = await self._get_chat(session, Group, group_id)

            if member and group:
                group.members.append(member)
                await session.commit()
            elif member is None:
                print(f"No member found - id {member_id}")
            elif group is None:
                print(f"No group found - id {group_id}")

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
