from typing import Optional
from datetime import datetime
from uuid import UUID

import sqlalchemy as sqla
from sqlalchemy.orm import Mapped, mapped_column
from src.database.relational import Base


class DatabaseDictionary(Base):
    __abstract__ = True
    __table_args__ = {'schema': 'dicts'}

    id: Mapped[int] = mapped_column(primary_key=True)
    display_name: Mapped[str] = mapped_column(sqla.String(length=255))
    description: Mapped[Optional[str]] = mapped_column(sqla.String(length=1000))
    is_active: Mapped[bool] = mapped_column(server_default=sqla.text('false'))
    is_system_value: Mapped[bool] = mapped_column(server_default=sqla.text('false'))
    create_date: Mapped[datetime] = mapped_column(server_default=sqla.text('now()'))
    created_by_id: Mapped[UUID] = mapped_column(sqla.ForeignKey('employees.id'))
    last_modified_by_id: Mapped[Optional[UUID]] = mapped_column(sqla.ForeignKey('employees.id'))
    last_modified_date: Mapped[Optional[datetime]]


class ApplicationRoles(DatabaseDictionary):
    __tablename__ = 'application_roles'


class SpecialistsRoles(DatabaseDictionary):
    __tablename__ = 'specialists_roles'


class ExaminationStatus(DatabaseDictionary):
    __tablename__ = 'examination_status'


class DrawnSpotsTypes(DatabaseDictionary):
    __tablename__ = 'drawn_spots_types'
