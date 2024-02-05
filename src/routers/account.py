from typing import Annotated

from fastapi import APIRouter, status, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm

from src.services.authentication import authenticate, add_token
import src.data_access_layer.general as dal_gen

router = APIRouter(tags=['employees_account'])

AsyncSessionDep = Annotated[dal_gen.db_rel.AsyncSession, Depends(dal_gen.get_relational_async_session)]
AuthDep = Annotated[OAuth2PasswordRequestForm, Depends(OAuth2PasswordRequestForm)]


@router.post('/employees/login')
async def create_token(authentication_data: AuthDep, session: AsyncSessionDep):
    email = authentication_data.username
    password = authentication_data.password
    async with session.begin():
        id_, role_id = await authenticate(email, password, session)
        if id_ is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        access_token = await add_token(id_, role_id, session)
    return {'access_token': access_token, 'token_type': 'bearer'}
