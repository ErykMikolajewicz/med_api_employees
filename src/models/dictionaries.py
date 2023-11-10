from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class Row(BaseModel):
    display_name: str = Field(min_length=2, max_length=255)
    description: str = Field(max_length=1000)
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class NewRow(Row):
    is_system_value: bool


class RowLocation(NewRow):
    location: str


class RowUpdate(BaseModel):
    display_name: Optional[str] = Field(None, min_length=2, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    is_active: Optional[bool] = Field(None)

    model_config = ConfigDict(from_attributes=True)
