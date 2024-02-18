from datetime import datetime, time, date
from typing import Optional
from uuid import UUID

import sqlalchemy as sqla
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column
from src.database.relational import Base


class Employees(Base):
    __tablename__ = 'employees'
    __table_args__ = (
        sqla.UniqueConstraint('telephone'),
        sqla.UniqueConstraint('business_telephone'),
        sqla.UniqueConstraint('email'),
        sqla.UniqueConstraint('pesel_or_identifier'),

        sqla.CheckConstraint('telephone is not null or business_telephone is not null')
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, server_default=sqla.text('gen_random_uuid()'))
    name: Mapped[str] = mapped_column(sqla.String(length=150))
    surname: Mapped[str] = mapped_column(sqla.String(length=255))
    pesel_or_identifier: Mapped[str] = mapped_column(sqla.String(length=36))
    birth_date: Mapped[date]
    role_id: Mapped[int] = mapped_column(sqla.ForeignKey('dicts.application_roles.id'))
    hashed_password: Mapped[bytearray] = mapped_column(sqla.LargeBinary(256))
    telephone: Mapped[Optional[str]] = mapped_column(sqla.String(15))
    business_telephone: Mapped[Optional[str]] = mapped_column(sqla.String(15))
    email: Mapped[str] = mapped_column(sqla.String(255))
    address: Mapped[str] = mapped_column(sqla.String(500))
    create_date: Mapped[datetime] = mapped_column(server_default=sqla.text('now()'))
    created_by_id: Mapped[UUID] = mapped_column(sqla.ForeignKey('employees.id'))
    last_modified_by_id: Mapped[Optional[UUID]] = mapped_column(sqla.ForeignKey('employees.id'))
    last_modified_date: Mapped[Optional[datetime]]


class EmployeesAccessTokens(Base):
    __tablename__ = 'employees_access_tokens'

    access_token: Mapped[str] = mapped_column(sqla.String(255), primary_key=True)
    id: Mapped[UUID] = mapped_column(sqla.ForeignKey('employees.id'))
    role_id: Mapped[int] = mapped_column(sqla.ForeignKey('dicts.application_roles.id'))
    expiration_date: Mapped[datetime]


class PatientsSpecialists(Base):
    __tablename__ = 'patients_specialists'

    id: Mapped[UUID] = mapped_column(sqla.ForeignKey('employees.id'), primary_key=True)
    role_id: Mapped[int] = mapped_column(sqla.ForeignKey('dicts.specialists_roles.id'))


class SpecialistsWorkingTime(Base):
    __tablename__ = 'specialists_working_time'
    __table_args__ = (
        sqla.CheckConstraint('day_of_week_id BETWEEN 1 AND 7'),
    )

    specialist_id: Mapped[UUID] = mapped_column(sqla.ForeignKey('patients_specialists.id'), primary_key=True)
    day_of_week_id: Mapped[int] = mapped_column(primary_key=True)
    accepted_visit_duration = mapped_column(ARRAY(sqla.Integer))
    work_start: Mapped[time]
    work_end: Mapped[time]
    work_break_start: Mapped[Optional[time]]
    work_break_end: Mapped[Optional[time]]
    is_working_day: Mapped[bool]


class IndividualWorkingBreaks(Base):
    __tablename__ = 'individual_working_breaks'

    break_id: Mapped[UUID] = mapped_column(primary_key=True, server_default=sqla.text('gen_random_uuid()'))
    specialist_id: Mapped[UUID] = mapped_column(sqla.ForeignKey('patients_specialists.id'))
    work_break_start: Mapped[datetime]
    work_break_end: Mapped[datetime]


class DrawnSpots(Base):
    __tablename__ = 'drawn_spots'

    id: Mapped[UUID] = mapped_column(primary_key=True, server_default=sqla.text('gen_random_uuid()'))
    location: Mapped[str] = mapped_column(sqla.String(length=255))
    type_id: Mapped[int] = mapped_column(sqla.ForeignKey('dicts.drawn_spots_types.id'))


class DrawnSpotsWorkHours(Base):
    __tablename__ = 'drawn_spots_work_hour'
    __table_args__ = (
        sqla.CheckConstraint('day_of_week_id BETWEEN 1 AND 7'),
    )

    drawn_spot_id: Mapped[UUID] = mapped_column(sqla.ForeignKey('drawn_spots.id'), primary_key=True)
    day_of_week_id: Mapped[int] = mapped_column(primary_key=True)
    work_start: Mapped[datetime]
    work_end: Mapped[datetime]


class DrawnSpotsGeneralHolidays(Base):
    __tablename__ = 'drawn_spots_general_holidays'

    holiday_date: Mapped[date] = mapped_column(primary_key=True)


class ExaminationsList(Base):
    __tablename__ = 'examinations_list'
    __table_args__ = (
        sqla.UniqueConstraint('examination_name'),
    )

    examination_id: Mapped[UUID] = mapped_column(primary_key=True)
    examination_name: Mapped[str] = mapped_column(sqla.String(255))
