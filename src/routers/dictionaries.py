from typing import Annotated, Any, Sequence, Optional

from fastapi import APIRouter, status, Depends, HTTPException, Response, Request, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

import src.services.authentication as auth
import src.data_access_layer.dictionaries as dal_dict
import src.data_access_layer.general as dal_gen
import src.models.dictionaries as mod_dict
from src.services.general import prepare_value_object, add_modification_info


def get_dictionary(dictionary_name: str, request: Request):
    db_dictionary = dal_dict.Dictionaries.get_db_dictionary(dictionary_name)
    if db_dictionary is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    else:
        request.state.dictionary = db_dictionary


AsyncSessionDep = Annotated[AsyncSession, Depends(dal_gen.get_relational_async_session)]
router = APIRouter(tags=['dictionaries'], dependencies=[Depends(auth.validate_token), Depends(get_dictionary)])


@router.post('/dictionaries/{dictionary_name}/{row_id}', status_code=status.HTTP_201_CREATED,
             response_model=mod_dict.Row)
async def add_row(row_id: Annotated[int, Path(gt=0)], dictionary_name: str, dictionary_row: mod_dict.Row,
                  session: AsyncSessionDep, request: Request, response: Response) -> dal_dict.DbDictionary:
    dictionary_row: dict[str, Any] = dictionary_row.model_dump()
    user_id = request.state.token.id
    db_dictionary = request.state.dictionary
    dictionary_row = prepare_value_object(dictionary_row, user_id, row_id)
    async with session.begin():
        data_access = dal_dict.Dictionaries(session)
        try:
            new_dictionary_row = await data_access.add_row(db_dictionary, dictionary_row)
        except IntegrityError:
            raise HTTPException(status_code=400, detail='introduced data violate database constraints.')
    if new_dictionary_row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    response.headers['Location'] = f'/dictionaries/{dictionary_name}/{row_id}'
    return new_dictionary_row


@router.get('/dictionaries/{dictionary_name}', status_code=status.HTTP_200_OK,
            response_model=Sequence[mod_dict.RowLocation])
async def get_rows(dictionary_name: str, session: AsyncSessionDep, request: Request, is_active: Optional[bool] = None)\
                   -> Sequence[dal_dict.DbDictionary]:
    db_dictionary = request.state.dictionary
    async with session.begin():
        data_access = dal_dict.Dictionaries(session)
        dictionary_rows = await data_access.get_rows(db_dictionary, is_active)
    if dictionary_rows is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    for row in dictionary_rows:
        row.location = f'/dictionaries/{dictionary_name}/{row.id}'
    return dictionary_rows


@router.delete('/dictionaries/{dictionary_name}/{row_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_row(row_id: int, session: AsyncSessionDep, request: Request) -> None:
    db_dictionary = request.state.dictionary
    async with session.begin():
        data_access = dal_dict.Dictionaries(session)
        dictionary_row = await data_access.get_row(db_dictionary, row_id)
        if dictionary_row is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        else:
            if dictionary_row.is_system_value:
                message = 'Can not remove system value contact with developer team to make changes in application.'
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST(message))
            else:
                await data_access.delete_row(db_dictionary, row_id)


@router.patch('/dictionaries/{dictionary_name}/{row_id}', status_code=status.HTTP_200_OK,
              response_model=mod_dict.Row)
async def update_row(row_data: mod_dict.RowUpdate, row_id: int, session: AsyncSessionDep, request: Request)\
                    -> dal_dict.DbDictionary:
    db_dictionary = request.state.dictionary
    row_update: dict[str, Any] = row_data.model_dump(exclude_none=True)
    user_id = request.state.token.id
    row_update = add_modification_info(row_update, user_id)
    async with session.begin():
        data_access = dal_dict.Dictionaries(session)
        dictionary_row = await data_access.update_row(db_dictionary, row_update, row_id)
    if dictionary_row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    else:
        return dictionary_row
