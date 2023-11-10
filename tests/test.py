from typing import Any

import httpx
import pytest
import pytest_asyncio
from fastapi import status

from data_fixtures import employee_data, dictionary_data, secrets, string_creator


@pytest.mark.asyncio
class TestEmployeesEndpoints:
    added_employees = []

    @staticmethod
    @pytest_asyncio.fixture(autouse=True, scope='class')
    async def log_as_administrator(log_as):
        administrator_login = secrets['administrator_login']
        administrator_password = secrets['administrator_password']
        login_data = await log_as(administrator_login, administrator_password)
        admin_token = login_data['access_token']
        TestEmployeesEndpoints.admin_token = admin_token

    @pytest.mark.parametrize("invalid_date", ["0000-00-00", "2077-01-01", "2000-13-12", None])
    async def test_add_invalid_date(self, invalid_date, test_client: httpx.AsyncClient, request,
                                    employee_data: dict[str, Any]):
        employee_data['birth_date'] = invalid_date
        auth_token = request.cls.admin_token
        response = await test_client.post("/employees", json=employee_data,
                                          headers={'Authorization': 'Bearer ' + auth_token})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.parametrize("invalid_phone_number", ["abcd", "564 675 311", "+45643117", "611-743-222", "8874303654"])
    async def test_add_invalid_phone_number(self, invalid_phone_number, test_client: httpx.AsyncClient, request,
                                            employee_data: dict[str, Any]):
        employee_data['telephone'] = invalid_phone_number
        auth_token = request.cls.admin_token
        response = await test_client.post("/employees", json=employee_data,
                                          headers={'Authorization': 'Bearer ' + auth_token})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.parametrize("invalid_password", ["Everybody lies.", "password123", "<?%$#@#"])
    async def test_add_invalid_password(self, invalid_password, test_client: httpx.AsyncClient, request,
                                        employee_data: dict[str, Any]):
        employee_data['password'] = invalid_password
        employee_data['confirm_password'] = invalid_password
        auth_token = request.cls.admin_token
        response = await test_client.post("/employees", json=employee_data,
                                          headers={'Authorization': 'Bearer ' + auth_token})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.parametrize("not_matching_password", ["Everybody lies2.", "Password123", "A2<?%$#@#"])
    async def test_add_not_matching_password(self, not_matching_password, test_client: httpx.AsyncClient, request,
                                             employee_data: dict[str, Any]):
        employee_data['confirm_password'] = not_matching_password
        auth_token = request.cls.admin_token
        response = await test_client.post("/employees", json=employee_data,
                                          headers={'Authorization': 'Bearer ' + auth_token})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.parametrize("missing_field", ["name", "surname", "role_id", "pesel_or_identifier", "email", "address"])
    async def test_add_missing_field(self, missing_field, test_client: httpx.AsyncClient, request,
                                     employee_data: dict[str, Any]):
        employee_data[missing_field] = None
        auth_token = request.cls.admin_token
        response = await test_client.post("/employees", json=employee_data,
                                          headers={'Authorization': 'Bearer ' + auth_token})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.parametrize("field, invalid_length", [("name", 156), ("surname", 256), ('pesel_or_identifier', 37),
                                                       ('email', 256), ('address', 501)])
    async def test_add_too_length_field(self, invalid_length, field, test_client: httpx.AsyncClient, request,
                                        string_creator, employee_data: dict[str, Any]):
        to_length_data = string_creator(invalid_length)
        employee_data[field] = to_length_data
        auth_token = request.cls.admin_token
        response = await test_client.post("/employees", json=employee_data,
                                          headers={'Authorization': 'Bearer ' + auth_token})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.parametrize("field, invalid_length", [("name", 1), ("surname", 1), ('pesel_or_identifier', 6),
                                                       ('email', 4)])
    async def test_add_too_short_field(self, invalid_length, field, test_client: httpx.AsyncClient, request,
                                       string_creator, employee_data: dict[str, Any]):
        to_length_data = string_creator(invalid_length)
        employee_data[field] = to_length_data
        auth_token = request.cls.admin_token
        response = await test_client.post("/employees", json=employee_data,
                                          headers={'Authorization': 'Bearer ' + auth_token})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_add_employee(self, test_client: httpx.AsyncClient, request, employee_data: dict[str, Any]):
        auth_token = request.cls.admin_token
        response = await test_client.post("/employees", json=employee_data,
                                          headers={'Authorization': 'Bearer ' + auth_token})
        location = response.headers.get('location')
        request.cls.added_employees.append(location)
        assert response.status_code == status.HTTP_201_CREATED

    async def test_get_employees(self, test_client: httpx.AsyncClient, request, employee_data: dict[str, Any]):
        auth_token = request.cls.admin_token
        response = await test_client.get("/employees", headers={'Authorization': 'Bearer ' + auth_token},
                                         params={"pagination": {"page-number": 1, "page-size": 10}})
        assert response.status_code == status.HTTP_200_OK

    async def test_update_employee(self, test_client: httpx.AsyncClient, request):
        auth_token = request.cls.admin_token
        employee_update_location = request.cls.added_employees[0]
        employee_data = {'name': 'Greg'}
        response = await test_client.patch(employee_update_location, json=employee_data,
                                           headers={'Authorization': 'Bearer ' + auth_token})
        updated_employee = response.json()
        assert employee_data['name'] == updated_employee['name']
        assert response.status_code == status.HTTP_200_OK

    async def test_delete_employee(self, test_client: httpx.AsyncClient, request):
        auth_token = request.cls.admin_token
        employee_delete_location = request.cls.added_employees[0]
        response = await test_client.delete(employee_delete_location, headers={'Authorization': 'Bearer ' + auth_token})
        assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.asyncio
class TestDictionariesEndpoints:
    added_dictionary_rows = []

    @staticmethod
    @pytest_asyncio.fixture(autouse=True, scope='class')
    async def log_as_administrator(log_as):
        administrator_login = secrets['administrator_login']
        administrator_password = secrets['administrator_password']
        login_data = await log_as(administrator_login, administrator_password)
        admin_token = login_data['access_token']
        TestDictionariesEndpoints.admin_token = admin_token

    @pytest.mark.parametrize("invalid_id", [-1, "id"])
    async def test_add_invalid_dictionary_id(self, invalid_id, test_client: httpx.AsyncClient, request,
                                             dictionary_data: dict[str, Any]):
        auth_token = request.cls.admin_token
        response = await test_client.post(f"/dictionaries/application_roles/{invalid_id}", json=dictionary_data,
                                          headers={'Authorization': 'Bearer ' + auth_token})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.parametrize("invalid_name", [53, False, ["name"], {"display_name": "new_name"}])
    async def test_add_invalid_name(self, invalid_name, test_client: httpx.AsyncClient, request,
                                    dictionary_data: dict[str, Any]):
        dictionary_data['display_name'] = invalid_name
        auth_token = request.cls.admin_token
        response = await test_client.post("/dictionaries/application_roles/1030", json=dictionary_data,
                                          headers={'Authorization': 'Bearer ' + auth_token})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.parametrize("invalid_description", [0, True, ["^^^"]])
    async def test_add_invalid_description(self, invalid_description, test_client: httpx.AsyncClient, request,
                                           dictionary_data: dict[str, Any]):
        dictionary_data['description'] = invalid_description
        auth_token = request.cls.admin_token
        response = await test_client.post("/dictionaries/application_roles/1030", json=dictionary_data,
                                          headers={'Authorization': 'Bearer ' + auth_token})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_add_invalid_is_active(self, test_client: httpx.AsyncClient, request,
                                         dictionary_data: dict[str, Any]):
        dictionary_data['is_active'] = "null"
        auth_token = request.cls.admin_token
        response = await test_client.post("/dictionaries/application_roles/1030", json=dictionary_data,
                                          headers={'Authorization': 'Bearer ' + auth_token})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.parametrize("field, invalid_length", [("display_name", 256), ("description", 1001)])
    async def test_add_too_length_field(self, invalid_length, field, test_client: httpx.AsyncClient, request,
                                        string_creator, dictionary_data: dict[str, Any]):
        to_length_data = string_creator(invalid_length)
        dictionary_data[field] = to_length_data
        auth_token = request.cls.admin_token
        response = await test_client.post("/dictionaries/application_roles/1030", json=dictionary_data,
                                          headers={'Authorization': 'Bearer ' + auth_token})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_add_too_short_name(self, test_client: httpx.AsyncClient, request, string_creator,
                                      dictionary_data: dict[str, Any]):
        to_length_data = string_creator(1)
        dictionary_data['display_name'] = to_length_data
        auth_token = request.cls.admin_token
        response = await test_client.post("/dictionaries/application_roles/1030", json=dictionary_data,
                                          headers={'Authorization': 'Bearer ' + auth_token})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_add_dictionary_row(self, test_client: httpx.AsyncClient, request, dictionary_data: dict[str, Any]):
        auth_token = request.cls.admin_token
        response = await test_client.post("/dictionaries/application_roles/1030", json=dictionary_data,
                                          headers={'Authorization': 'Bearer ' + auth_token})
        location = response.headers.get('location')
        request.cls.added_dictionary_rows.append(location)
        assert response.status_code == status.HTTP_201_CREATED

    async def test_get_dictionary_rows(self, test_client: httpx.AsyncClient, request, dictionary_data: dict[str, Any]):
        auth_token = request.cls.admin_token
        response = await test_client.get("/dictionaries/application_roles",
                                         headers={'Authorization': 'Bearer ' + auth_token})
        assert response.status_code == status.HTTP_200_OK

    async def test_update_dictionary_row(self, test_client: httpx.AsyncClient, request):
        auth_token = request.cls.admin_token
        dictionary_row_location = request.cls.added_dictionary_rows[0]
        dictionary_row_data = {'display_name': 'Update dictionary row test'}
        response = await test_client.patch(dictionary_row_location, json=dictionary_row_data,
                                           headers={'Authorization': 'Bearer ' + auth_token})
        updated_dictionary_row = response.json()
        assert dictionary_row_data['display_name'] == updated_dictionary_row['display_name']
        assert response.status_code == status.HTTP_200_OK

    async def test_delete_dictionary(self, test_client: httpx.AsyncClient, request):
        auth_token = request.cls.admin_token
        dictionary_location = request.cls.added_dictionary_rows[0]
        response = await test_client.delete(dictionary_location, headers={'Authorization': 'Bearer ' + auth_token})
        assert response.status_code == status.HTTP_204_NO_CONTENT
