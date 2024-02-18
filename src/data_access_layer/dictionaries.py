from typing import Any, Sequence, TypeVar

from sqlalchemy import insert, select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import or_

import src.database.dicts_models as db_dicts

DbDictionary = TypeVar('DbDictionary', bound=db_dicts.DatabaseDictionary)


class Dictionaries:

    __db_dictionaries_by_names = {'application_roles': db_dicts.ApplicationRoles,
                                  'specialists_roles': db_dicts.SpecialistsRoles,
                                  'examination_status': db_dicts.ExaminationStatus,
                                  'drawn_spots_types': db_dicts.DrawnSpotsTypes}

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

    async def get_rows(self, db_dictionary: DbDictionary, is_active: bool) -> Sequence[DbDictionary]:
        select_query = select(db_dictionary).where(or_(is_active is None, db_dictionary.is_active == is_active))
        dictionary_rows = await self.db_session.scalars(select_query)
        dictionary_rows = dictionary_rows.all()
        return dictionary_rows

    async def get_row(self, db_dictionary: DbDictionary, row_id: int) -> DbDictionary:
        select_query = select(db_dictionary).where(db_dictionary.id == row_id)
        dictionary_row = await self.db_session.scalar(select_query)
        return dictionary_row

    async def delete_row(self, db_dictionary: DbDictionary, row_id: int):
        delete_query = delete(db_dictionary).where(db_dictionary.id == row_id)
        await self.db_session.execute(delete_query)
        await self.db_session.flush()

    async def update_row(self, db_dictionary: DbDictionary, row_data: dict[str, Any],  row_id: int) -> DbDictionary:
        update_query = update(db_dictionary).where(db_dictionary.id == row_id).values(row_data).returning(db_dictionary)
        dictionary_row = await self.db_session.scalar(update_query)
        await self.db_session.flush()
        return dictionary_row
