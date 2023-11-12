import hashlib
import os
import secrets
import datetime
import random
import string
from uuid import UUID
from typing import Annotated

from fastapi import Depends, status, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.data_access_layer.employees import Employees, EmployeesTokens
from src.data_access_layer.general import get_relational_async_session

Token = Annotated[str, Depends(OAuth2PasswordBearer(tokenUrl="/employees/login"))]

salt_file = os.environ["SALT_FILE"]
with open(salt_file, 'r') as file:
    salt = file.read()


def hash_password(password: str) -> bytes:
    password_with_salt = salt + password
    hash_ = hashlib.sha256(password_with_salt.encode("utf-8"))
    hashed_password = hash_.digest()
    return hashed_password


def generate_token() -> str:
    token = secrets.token_urlsafe(32)
    return token


def get_expiration_date(expiration_in_minutes: int = 1_440) -> datetime.datetime:
    return datetime.datetime.now() + datetime.timedelta(minutes=expiration_in_minutes)


def verify_password(password: str, hashed_password: str) -> bool:
    to_check = hash_password(password)
    return to_check == hashed_password


def create_and_hash_random_password() -> (int, bytes):
    letters = string.ascii_letters
    password = ''
    for i in range(33):
        random_value = random.randint(0, 51)
        password += letters[random_value]
    big_letters = string.ascii_uppercase
    random_value = random.randint(0, 25)
    password += big_letters[random_value]
    password += str(random_value)
    password_hash = hash_password(password)
    return password, password_hash


async def authenticate(email: str, password: str, session: AsyncSession) -> tuple[int, int] | None:
    data_access = Employees(session)
    employee = await data_access.get_by_email(email)
    if verify_password(password, employee.hashed_password):
        return employee.id, employee.role_id


async def add_token(id_: UUID, role_id: int, session: AsyncSession) -> str:
    data_access = EmployeesTokens(session)
    new_token = generate_token()
    expiration_date = get_expiration_date()
    token_data = {'id': id_, 'access_token': new_token, 'role_id': role_id, 'expiration_date': expiration_date}
    await data_access.add(token_data)
    return new_token


async def validate_token(token: Token, request: Request) -> (UUID, int):
    session = get_relational_async_session()
    async with session.begin():
        data_access = EmployeesTokens(session)
        token_data = await data_access.check(token)
    if token_data is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    request.state.token = token_data
