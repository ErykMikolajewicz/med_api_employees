from datetime import datetime, date
from typing import Optional
from uuid import UUID

import sqlalchemy as sqla
from sqlalchemy.orm import Mapped, mapped_column
from src.databases.relational import Base


class Patients(Base):
    __tablename__ = 'patients'
    __table_args__ = (
        sqla.UniqueConstraint('login'),

        # To achieve distinct after verification and prevent mean blocking fields by registering fictional data
        sqla.UniqueConstraint('pesel_or_identifier', 'is_verified'),
        sqla.UniqueConstraint('telephone', 'telephone_verified'),
        sqla.UniqueConstraint('email', 'email_verified'),
        sqla.CheckConstraint('is_verified != false and telephone_verified != false and email_verified != false'),

        {'schema': 'patients'}
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, server_default=sqla.text('gen_random_uuid()'))
    login: Mapped[str] = mapped_column(sqla.String(255))
    hashed_password: Mapped[bytearray] = mapped_column(sqla.LargeBinary(256))
    name: Mapped[str] = mapped_column(sqla.String(length=150))
    surname: Mapped[str] = mapped_column(sqla.String(length=255))
    sex: Mapped[str] = mapped_column(sqla.String(length=10))
    pesel_or_identifier: Mapped[str] = mapped_column(sqla.String(length=36))
    birth_date: Mapped[date]
    telephone: Mapped[Optional[str]] = mapped_column(sqla.String(15))
    email: Mapped[Optional[str]] = mapped_column(sqla.String(255))
    address: Mapped[str]
    create_date: Mapped[datetime] = mapped_column(server_default=sqla.text('now()'))
    is_verified: Mapped[Optional[bool]]  # Null before verification, for distinct treatment in unique
    telephone_verified: Mapped[Optional[bool]]
    email_verified: Mapped[Optional[bool]]


class Appointments(Base):
    __tablename__ = 'appointments'
    __table_args__ = (
        sqla.UniqueConstraint('start', 'patient_id'),
        {'postgresql_partition_by': 'RANGE (start)', 'schema': 'patients'}
    )

    id: Mapped[UUID] = mapped_column(server_default=sqla.text('gen_random_uuid()'))
    patient_id: Mapped[UUID] = mapped_column(sqla.ForeignKey("patients.patients.id"))
    start: Mapped[datetime] = mapped_column(primary_key=True)
    end: Mapped[datetime]
    specialist_id: Mapped[UUID] = mapped_column(sqla.ForeignKey("patients_specialists.id"), primary_key=True)


class PatientsAccessTokens(Base):
    __tablename__ = 'patients_access_tokens'
    __table_args__ = {'schema': 'patients'}

    access_token: Mapped[str] = mapped_column(sqla.String(255), primary_key=True)
    id: Mapped[UUID] = mapped_column(sqla.ForeignKey("patients.patients.id"))
    expiration_date: Mapped[datetime]


class VerifyEmail(Base):
    __tablename__ = 'verify_email'
    __table_args__ = {'schema': 'patients'}

    verification_string: Mapped[str] = mapped_column(sqla.String(255), primary_key=True)
    patient_id: Mapped[UUID]
    verification_time: Mapped[datetime]
