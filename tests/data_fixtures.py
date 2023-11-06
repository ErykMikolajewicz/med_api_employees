import json

import pytest

from tests.application_roles import DOCTOR_ID


@pytest.fixture(scope="function")
def employee_data():
    employee_data = {
        "name": "Gregory",
        "surname": "House",
        "role_id": DOCTOR_ID,
        "pesel_or_identifier": "House",
        "birth_date": "1959-05-11",
        "telephone": "740504105",
        "business_telephone": "+1708624738",
        "email": "gregory.house@medapp.com",
        "address": "221B Baker Street",
        "password": "LOVE SUCKS </3",
        "confirm_password": "LOVE SUCKS </3"
    }

    yield employee_data


with open('./tests/secrets.json', 'r') as file:
    secrets = json.load(file)

