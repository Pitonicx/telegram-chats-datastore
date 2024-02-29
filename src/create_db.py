from db_helper import db_helper
from core import Base
import asyncio


async def create_tables(engine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


if __name__ == "__main__":
    asyncio.run(create_tables(db_helper.engine))
