from asyncio import DefaultEventLoopPolicy

import pytest
import pytest_asyncio
import httpx
from authlib.integrations.httpx_client import AsyncOAuth2Client


@pytest.fixture(scope="session")
def event_loop_policy(request):
    return DefaultEventLoopPolicy()


@pytest_asyncio.fixture
async def test_client():
    async with httpx.AsyncClient(base_url="http://localhost:8009") as test_client:
        yield test_client


@pytest_asyncio.fixture(scope='session')
async def log_as():

    async def log(email: str, password: str):
        authentication_client = AsyncOAuth2Client()
        token = await authentication_client.fetch_token('http://127.0.0.1:8009/employees/login', username=email,
                                                        password=password)
        return token
    
    yield log
