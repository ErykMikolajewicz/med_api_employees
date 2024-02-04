from contextlib import asynccontextmanager
import ssl

from fastapi import FastAPI
from fastapi.responses import RedirectResponse

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

ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ssl_context.load_cert_chain('./certificate.pem', keyfile='./privatekey.pem')

app.include_router(src.routers.account.router)
app.include_router(src.routers.employees.router)
app.include_router(src.routers.dictionaries.router)
app.include_router(src.routers.patients.router)


@app.get("/", response_class=RedirectResponse)  # to see docs after click startup link
async def redirect_fastapi():
    return "https://localhost:8009/docs"
