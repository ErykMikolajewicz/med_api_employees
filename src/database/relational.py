import os

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase


POSTGRES_PASSWORD_FILE = os.environ['POSTGRES_PASSWORD_FILE']
with open(POSTGRES_PASSWORD_FILE, 'r') as file:
    postgres_password = file.read()

ENV = os.environ['ENV']
if ENV == 'LOCAL':
    host = 'localhost/postgres'
elif ENV == 'DOCKER':
    host = 'postgres_database/postgres'
else:
    raise Exception('Invalid environment config!')

user = 'postgres'
driver = 'postgresql+asyncpg'

DATABASE_URL = f'{driver}://{user}:{postgres_password}@{host}'

async_engine = create_async_engine(DATABASE_URL, echo=True)
async_session = async_sessionmaker(async_engine, expire_on_commit=False, class_=AsyncSession)


class Base(DeclarativeBase):
    pass

