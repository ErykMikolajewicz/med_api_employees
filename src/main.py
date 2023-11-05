from fastapi import FastAPI
from contextlib import asynccontextmanager
import uvicorn

from src.data_access_layer.general import init_relational_database, close_relational_database
import src.routers.employees
import src.routers.patients
import src.routers.account
import src.routers.dictionaries


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_relational_database()
    yield
    await close_relational_database()

app = FastAPI(lifespan=lifespan)

app.include_router(src.routers.account.router)
app.include_router(src.routers.employees.router)
app.include_router(src.routers.dictionaries.router)
app.include_router(src.routers.patients.router)


def main():
    uvicorn.run(app, host='0.0.0.0', port=8009)


if __name__ == '__main__':
    main()

