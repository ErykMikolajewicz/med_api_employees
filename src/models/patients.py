from typing import Optional
import datetime

from pydantic import BaseModel, Field


class Patient(BaseModel):
    login: str = Field(min_length=2, max_length=155)
    name: str = Field(min_length=2, max_length=155)
    surname: str = Field(min_length=2, max_length=255)
    telephone: Optional[str] = Field(None, min_length=9, max_length=13, pattern=r'^\+?\d{9,12}$')
    email: Optional[str] = Field(None, min_length=5, max_length=255)
    address: Optional[str] = Field(None)
    sex: int = Field(gt=0)
    pesel_or_identifier: str = Field(min_length=3, max_length=36)
    birth_date: datetime.date
