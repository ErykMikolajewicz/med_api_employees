import json
import random
import string
from typing import Callable

import pytest

from tests.application_roles import DOCTOR_ID

with open('./tests/secrets.json', 'r') as file:
    secrets = json.load(file)


@pytest.fixture(scope="function")
def employee_data():
    employee_data = {
        "name": "Gregory",
        "surname": "House",
        "role_id": DOCTOR_ID,
        "pesel_or_identifier": "Dr House",
        "birth_date": "1959-05-11",
        "telephone": "740504105",
        "business_telephone": "+1708624738",
        "email": "gregory.house@medapp.com",
        "address": "221B Baker Street",
        "password": "LOVE SUCKS </3",
        "confirm_password": "LOVE SUCKS </3"
    }

    yield employee_data


@pytest.fixture(scope="function")
def dictionary_data():
    dictionary_data = {
        "display_name": "string",
        "description": "string",
        "is_active": True
    }

    yield dictionary_data


@pytest.fixture(scope="session", autouse=True)
def string_creator() -> Callable[[int], str]:

    def long_text(length: int) -> str:
        random_string = ""
        letters = [random.choice(string.ascii_letters) for _ in range(length)]
        random_string = random_string.join(letters)
        return random_string

    yield long_text
