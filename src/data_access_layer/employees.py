from typing import Any, Sequence
import datetime
from uuid import UUID

import src.database.models.employees
from sqlalchemy import update, insert, delete, select
from sqlalchemy.sql import func
from sqlalchemy.ext.asyncio import AsyncSession


class Employees:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def add(self, new_employee: dict[str, Any]) -> src.databases.models.employees.Employees:
        insert_query = insert(src.databases.models.employees.Employees).values(new_employee).returning(
            src.databases.models.employees.Employees)
        result = await self.db_session.scalar(insert_query)
        await self.db_session.flush()
        return result

    async def get_many(self, pagination: dict[str, int]) -> (Sequence[src.databases.models.employees.Employees], int):
        offset = pagination['offset']
        limit = offset + pagination['page_size']
        select_query = select(src.databases.models.employees.Employees).offset(offset).limit(limit)
        employees = await self.db_session.scalars(select_query)
        count_query = select(func.count(src.databases.models.employees.Employees.id).over())
        employees_number = await self.db_session.scalar(count_query)
        employees = employees.fetchall()
        return employees, employees_number

    async def get_by_email(self, email: str) -> src.databases.models.employees.Employees:
        select_query = select(src.databases.models.employees.Employees).where(
            src.databases.models.employees.Employees.email == email)
        result = await self.db_session.scalar(select_query)
        return result

    async def update(self, id_: UUID, employee: dict[str, Any]) -> src.databases.models.employees.Employees:
        update_query = update(src.databases.models.employees.Employees).where(
            src.databases.models.employees.Employees.id == id_)\
                       .values(employee).returning(src.databases.models.employees.Employees)
        result = await self.db_session.scalar(update_query)
        await self.db_session.flush()
        return result

    async def delete(self, id_: UUID) -> int:
        delete_query = delete(src.databases.models.employees.Employees).where(
            src.databases.models.employees.Employees.id == id_)
        delete_result = await self.db_session.execute(delete_query)
        number_deleted_rows: int = delete_result.rowcount # bad type hint for sqlalchemy
        await self.db_session.flush()
        return number_deleted_rows


class EmployeesTokens:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def add(self, new_token: dict[str, Any]):
        insert_query = insert(src.databases.models.employees.EmployeesAccessTokens).values(new_token)
        await self.db_session.execute(insert_query)
        await self.db_session.flush()

    async def check(self, access_token: str) -> src.databases.models.employees.EmployeesAccessTokens:
        select_query = (select(src.databases.models.employees.EmployeesAccessTokens).
                        where(src.databases.models.employees.EmployeesAccessTokens.access_token == access_token,
                              src.databases.models.employees.EmployeesAccessTokens.expiration_date > datetime.datetime.now()))
        token_data = await self.db_session.scalar(select_query)
        return token_data
