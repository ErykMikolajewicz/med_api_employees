from typing import Any, Sequence, cast
from uuid import UUID

from sqlalchemy import update, delete, select
from sqlalchemy.orm import defer
from sqlalchemy.ext.asyncio import AsyncSession

import src.databases.models as db_mod


class Patients:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def get_many(self, pagination: tuple[int, int]) -> Sequence[db_mod.Patients]:
        skip, limit = pagination
        select_query = select(db_mod.Patients).offset(skip).limit(limit).options(defer(db_mod.Patients.hashed_password))
        rows = await self.db_session.scalars(select_query)
        results = rows.all()
        return results

    async def update(self, id_: UUID, patient: dict[str, Any]) -> db_mod.Patients:
        update_query = update(db_mod.Patients).where(db_mod.Patients.id == id_)\
                       .values(patient).returning(db_mod.Patients)
        result = await self.db_session.scalar(update_query)
        await self.db_session.flush()
        return result
    
    async def delete_account(self, id_: UUID) -> int:
        delete_query = delete(db_mod.Patients).where(db_mod.Patients.id == id_)
        delete_result = await self.db_session.execute(delete_query)
        await self.db_session.flush()
        number_deleted_rows: int = cast(delete_result.rowcount, int)
        return number_deleted_rows
