from typing import Any, Sequence, cast
from uuid import UUID

from sqlalchemy import update, delete, select, insert, func
from sqlalchemy.ext.asyncio import AsyncSession

import src.databases.models as db_mod


class Patients:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def add(self, new_patient: dict[str, Any]) -> db_mod.Patients:
        insert_query = insert(db_mod.Patients).values(new_patient).returning(db_mod.Patients)
        result = await self.db_session.scalar(insert_query)
        await self.db_session.flush()
        return result

    async def get_many(self, pagination: dict[str, int]) -> (Sequence[db_mod.Patients], int):
        offset = pagination['offset']
        limit = offset + pagination['page_size']
        select_query = select(db_mod.Patients).offset(offset).limit(limit)
        patients = await self.db_session.scalars(select_query)
        count_query = select(func.count(db_mod.Patients.id).over())
        patients_number = await self.db_session.scalar(count_query)
        patients = patients.fetchall()
        return patients, patients_number

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

    async def get(self, patient_id) -> db_mod.Patients:
        select_query = select(db_mod.Patients).where(db_mod.Patients.id == patient_id)
        patient = await self.db_session.scalars(select_query)
        patient = patient.first()
        return patient
