from uuid import UUID
from datetime import date

import src.database.models.patients as db_mod_pat
from sqlalchemy import delete, select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession


class Appointments:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def delete(self, id_: UUID) -> (int, UUID):
        delete_query = (delete(db_mod_pat.Appointments).where(db_mod_pat.Appointments.id == id_).
                        returning(db_mod_pat.Appointments.patient_id, db_mod_pat.Appointments.start))
        delete_result = await self.db_session.execute(delete_query)
        visit_data = delete_result.first()
        number_deleted_rows: int = delete_result.rowcount # bad type hint for sqlalchemy
        await self.db_session.flush()
        return number_deleted_rows, visit_data

    async def get_many(self, pagination, specialist_id: UUID, start: date, end: date):
        offset = pagination['offset']
        limit = offset + pagination['page_size']
        select_query = (select(db_mod_pat.Appointments).offset(offset).limit(limit).
                        where(or_(db_mod_pat.Appointments.specialist_id == specialist_id, specialist_id is None)).
                        where(or_(db_mod_pat.Appointments.start == start, start is None)).
                        where(or_(db_mod_pat.Appointments.end == end, end is None)))
        appointments = await self.db_session.scalars(select_query)
        count_query = select(func.count(db_mod_pat.Appointments.id).over())
        appointments_number = await self.db_session.scalar(count_query)
        appointments = appointments.fetchall()
        return appointments, appointments_number
