import typing as typ
import datetime
from uuid import UUID

from sqlalchemy import update, insert, delete, select
from sqlalchemy.sql import func
from sqlalchemy.ext.asyncio import AsyncSession

import src.databases.models as db_mod


class Employees:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def add(self, new_employee: dict[str, typ.Any]) -> db_mod.Employees:
        insert_query = insert(db_mod.Employees).values(new_employee).returning(db_mod.Employees)
        result = await self.db_session.scalar(insert_query)
        await self.db_session.flush()
        return result

    async def get_many(self, pagination: dict[str, int]) -> (typ.Sequence[db_mod.Employees], int):
        offset = pagination['offset']
        limit = offset + pagination['page_size']
        select_query = select(db_mod.Employees).offset(offset).limit(limit)
        employees = await self.db_session.scalars(select_query)
        count_query = select(func.count(db_mod.Employees.id).over())
        employees_number = await self.db_session.scalar(count_query)
        employees = employees.fetchall()
        return employees, employees_number

    async def get_by_email(self, email: str) -> db_mod.Employees:
        select_query = select(db_mod.Employees).where(db_mod.Employees.email == email)
        result = await self.db_session.scalar(select_query)
        return result

    async def update(self, id_: UUID, employee: dict[str, typ.Any]) -> db_mod.Employees:
        update_query = update(db_mod.Employees).where(db_mod.Employees.id == id_)\
                       .values(employee).returning(db_mod.Employees)
        result = await self.db_session.scalar(update_query)
        await self.db_session.flush()
        return result

    async def delete(self, id_: UUID) -> int:
        delete_query = delete(db_mod.Employees).where(db_mod.Employees.id == id_)
        delete_result = await self.db_session.execute(delete_query)
        number_deleted_rows: int = delete_result.rowcount # bad type hint for sqlalchemy
        await self.db_session.flush()
        return number_deleted_rows


class EmployeesTokens:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def add(self, new_token: dict[str, typ.Any]):
        insert_query = insert(db_mod.EmployeesAccessTokens).values(new_token)
        await self.db_session.execute(insert_query)
        await self.db_session.flush()

    async def check(self, access_token: str) -> db_mod.EmployeesAccessTokens:
        select_query = (select(db_mod.EmployeesAccessTokens).
                        where(db_mod.EmployeesAccessTokens.access_token == access_token,
                              db_mod.EmployeesAccessTokens.expiration_date > datetime.datetime.now()))
        token_data = await self.db_session.scalar(select_query)
        return token_data
