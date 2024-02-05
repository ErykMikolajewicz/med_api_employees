from typing import Any, Sequence, cast
from uuid import UUID

import src.databases.models.patients
from sqlalchemy import update, delete, select, insert, func
from sqlalchemy.ext.asyncio import AsyncSession


class Patients:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def add(self, new_patient: dict[str, Any]) -> src.databases.models.patients.Patients:
        insert_query = insert(src.databases.models.patients.Patients).values(new_patient).returning(
            src.databases.models.patients.Patients)
        result = await self.db_session.scalar(insert_query)
        await self.db_session.flush()
        return result

    async def get_many(self, pagination: dict[str, int]) -> (Sequence[src.databases.models.patients.Patients], int):
        offset = pagination['offset']
        limit = offset + pagination['page_size']
        select_query = select(src.databases.models.patients.Patients).offset(offset).limit(limit)
        patients = await self.db_session.scalars(select_query)
        count_query = select(func.count(src.databases.models.patients.Patients.id).over())
        patients_number = await self.db_session.scalar(count_query)
        patients = patients.fetchall()
        return patients, patients_number

    async def update(self, id_: UUID, patient: dict[str, Any]) -> src.databases.models.patients.Patients:
        update_query = update(src.databases.models.patients.Patients).where(
            src.databases.models.patients.Patients.id == id_)\
                       .values(patient).returning(src.databases.models.patients.Patients)
        result = await self.db_session.scalar(update_query)
        await self.db_session.flush()
        return result
    
    async def delete_account(self, id_: UUID) -> int:
        delete_query = delete(src.databases.models.patients.Patients).where(
            src.databases.models.patients.Patients.id == id_)
        delete_result = await self.db_session.execute(delete_query)
        await self.db_session.flush()
        number_deleted_rows: int = cast(delete_result.rowcount, int)
        return number_deleted_rows

    async def get(self, patient_id) -> src.databases.models.patients.Patients:
        select_query = select(src.databases.models.patients.Patients).where(
            src.databases.models.patients.Patients.id == patient_id)
        patient = await self.db_session.scalars(select_query)
        patient = patient.first()
        return patient
