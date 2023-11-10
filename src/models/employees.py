from typing import Optional, Any
from datetime import date, timedelta

from pydantic import BaseModel, Field, ConfigDict, field_validator, model_validator


class Employee(BaseModel):
    name: str = Field(min_length=2, max_length=155)
    surname: str = Field(min_length=2, max_length=255)
    role_id: int = Field(gt=0)
    pesel_or_identifier: str = Field(min_length=7, max_length=36)
    birth_date: date
    telephone: Optional[str] = Field(None, min_length=9, max_length=13, pattern=r'^\+\d{10,12}|^\d{9}$')
    business_telephone: Optional[str] = Field(None, min_length=9, max_length=13, pattern=r'^\+\d{10,12}|^\d{9}$')
    email: str = Field(min_length=5, max_length=255)
    address: str = Field(max_length=500)

    model_config = ConfigDict(from_attributes=True)


class EmployeeLocation(Employee):
    location: str


class NewEmployee(Employee):
    password: str = Field(min_length=8, max_length=36, pattern=r'\d.*[A-Z]|[A-Z].*\d')
    confirm_password: str = Field(min_length=8, max_length=36, pattern=r'\d.*[A-Z]|[A-Z].*\d')

    @field_validator('birth_date')  # PyCharm raise warning, but it's follow Pydantic documentation
    @classmethod
    def valid_birthdate(cls, birth_date: date) -> date:
        life_span = timedelta(days=125 * 365)
        current_date = date.today()
        if birth_date < current_date - life_span:
            raise ValueError('Birth date to low!')
        elif birth_date > current_date:
            raise ValueError('Birth date to big!')
        return birth_date

    @model_validator(mode='before')  # PyCharm raise warning, but it's follow Pydantic documentation
    @classmethod
    def confirm_password(cls, values: Any) -> Any:
        try:
            password = values['password']
        except KeyError:
            raise ValueError('No password value')
        try:
            confirm_password = values['confirm_password']
        except KeyError:
            raise ValueError('No confirm password value')
        if password == confirm_password:
            return values
        else:
            raise ValueError('Passwords don\'t match!')


class EmployeeUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=155)
    surname: Optional[str] = Field(None, min_length=2, max_length=255)
    role_id: Optional[int] = Field(None, gt=0)
    pesel_or_identifier: Optional[str] = Field(None, min_length=7, max_length=36)
    birth_date: Optional[date] = Field(None)
    telephone: Optional[str] = Field(None, min_length=9, max_length=13, pattern=r'^\+?\d{9,12}$')
    business_telephone: Optional[str] = Field(None, min_length=9, max_length=13, pattern=r'^\+?\d{9,12}$')
    email: Optional[str] = Field(None, min_length=5, max_length=255)
    address: Optional[str] = Field(None, max_length=500)

    model_config = ConfigDict(from_attributes=True)
