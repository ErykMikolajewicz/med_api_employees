from uuid import UUID
from typing import Annotated

from fastapi import Depends, status, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer

from src.data_access_layer.employees import Employees, EmployeesTokens
from src.authentication.helpers import verify_password, generate_token, get_expiration_date
from src.data_access_layer.general import get_relational_async_session

session = get_relational_async_session()
Token = Annotated[str, Depends(OAuth2PasswordBearer(tokenUrl="/employees/login"))]


async def authenticate(email: str, password: str) -> tuple[int, int] | None:
    async with session.begin():
        data_access = Employees(session)
        employee = await data_access.get_by_email(email)
    if verify_password(password, employee.hashed_password):
        return employee.id, employee.role_id


async def add_token(id_: UUID, role_id: int) -> str:
    async with session.begin():
        data_access = EmployeesTokens(session)
        new_token = generate_token()
        expiration_date = get_expiration_date()
        token_data = {'id': id_, 'access_token': new_token, 'role_id': role_id, 'expiration_date': expiration_date}
        await data_access.add(token_data)
    return new_token


async def validate_token(token: Token, request: Request) -> (UUID, int):
    data_access = EmployeesTokens(session)
    async with session.begin():
        token_data = await data_access.check(token)
    if token_data is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    request.state.token = token_data
