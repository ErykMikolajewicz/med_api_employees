from typing import Any, Sequence, TypeVar, cast

from sqlalchemy import insert, select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.databases.dicts_models import DatabaseDictionary, ApplicationRoles

DbDictionary = TypeVar('DbDictionary', bound=DatabaseDictionary)


class Dictionaries:

    __db_dictionaries_by_names = {'application_roles': ApplicationRoles}

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    @classmethod
    def get_db_dictionary(cls, dictionary_name: str) -> DbDictionary | None:
        try:
            db_dictionary = cls.__db_dictionaries_by_names[dictionary_name]
            return db_dictionary
        except KeyError:
            return None

    async def add_row(self, db_dictionary: DbDictionary, dictionary_row: dict[str, Any]) -> DbDictionary:
        insert_query = insert(db_dictionary).values(dictionary_row).returning(db_dictionary)
        result = await self.db_session.scalar(insert_query)
        await self.db_session.flush()
        return result

    async def get_rows(self, db_dictionary: DbDictionary) -> Sequence[DbDictionary]:
        select_query = select(db_dictionary)
        dictionary_rows = await self.db_session.scalars(select_query)
        dictionary_rows = dictionary_rows.all()
        return dictionary_rows

    async def get_row(self, db_dictionary: DbDictionary, row_id: int) -> DbDictionary:
        select_query = select(db_dictionary).where(db_dictionary.id == row_id)
        dictionary_row = await self.db_session.scalar(select_query)
        return dictionary_row

    async def delete_row(self, db_dictionary: DbDictionary, row_id: int) -> int:
        delete_query = delete(db_dictionary).where(db_dictionary.id == row_id)
        delete_result = await self.db_session.execute(delete_query)
        number_deleted_rows: int = cast(delete_result.rowcount, int)
        await self.db_session.flush()
        return number_deleted_rows

    async def update_row(self, db_dictionary: DbDictionary, row_data: dict[str, Any],  row_id: int) -> DbDictionary:
        update_query = update(db_dictionary).where(db_dictionary.id == row_id).values(row_data).returning(db_dictionary)
        dictionary_row = await self.db_session.scalar(update_query)
        await self.db_session.flush()
        return dictionary_row
