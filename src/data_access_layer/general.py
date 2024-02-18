import sqlalchemy
from motor.motor_asyncio import AsyncIOMotorDatabase

import src.database.relational as db_rel


def get_relational_async_session() -> db_rel.AsyncSession:
    return db_rel.async_session()


async def init_relational_database():
    async with db_rel.async_engine.begin() as conn:
        await conn.execute(sqlalchemy.schema.CreateSchema('dicts', True))
        await conn.execute(sqlalchemy.schema.CreateSchema('patients', True))
        await conn.run_sync(db_rel.Base.metadata.create_all)


async def close_relational_database():
    await db_rel.async_engine.dispose(close=True)
