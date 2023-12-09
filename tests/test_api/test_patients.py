from typing import Any

import httpx
import pytest
import pytest_asyncio
from fastapi import status

from tests.data_fixtures import patient_data, secrets


@pytest.mark.asyncio
class TestPatientsEndpoints:
    added_employees = []

    @staticmethod
    @pytest_asyncio.fixture(autouse=True, scope='class')
    async def log_as_administrator(log_as):
        administrator_login = secrets['administrator_login']
        administrator_password = secrets['administrator_password']
        login_data = await log_as(administrator_login, administrator_password)
        admin_token = login_data['access_token']
        TestPatientsEndpoints.admin_token = admin_token

    async def test_get_empty_patients(self, test_client: httpx.AsyncClient, request):
        auth_token = request.cls.admin_token
        response = await test_client.get("/patients", headers={'Authorization': 'Bearer ' + auth_token},
                                         params={"pagination": {"page-number": 1, "page-size": 10}})
        assert response.status_code == status.HTTP_204_NO_CONTENT

    async def test_add_patient(self, test_client: httpx.AsyncClient, request, patient_data: dict[str, Any]):
        auth_token = request.cls.admin_token
        response = await test_client.post("/patients", json=patient_data,
                                          headers={'Authorization': 'Bearer ' + auth_token})
        location = response.headers.get('location')
        request.cls.added_employees.append(location)
        assert response.status_code == status.HTTP_201_CREATED

