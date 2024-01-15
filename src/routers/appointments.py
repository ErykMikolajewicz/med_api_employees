from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

import src.services.authentication as auth
import src.data_access_layer.appointments as dal_appointments
import src.data_access_layer.general as dal_gen
import src.models.general as mod_gen
from src.services.general import prepare_pagination_link

router = APIRouter(tags=['appointments'], dependencies=[Depends(auth.validate_token)])
AsyncSessionDep = Annotated[AsyncSession, Depends(dal_gen.get_relational_async_session)]


@router.delete("/appointments/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_appointment(appointment_id: UUID, session: AsyncSessionDep):
    async with session.begin():
        data_access = dal_appointments.Appointments(session)
        deleted_rows = await data_access.delete(appointment_id)
    if deleted_rows == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


@router.get("/appointments")
async def get_appointments(session: AsyncSessionDep, pagination: mod_gen.pagination_dependency,
                           specialist_id: UUID, start, end, response):
    async with session.begin():
        data_access = dal_appointments.Appointments(session)
        appointments, appointments_number = await data_access.get_many(pagination, specialist_id, start, end)
    if not appointments:
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT)
    for appointment in appointments:
        appointment.location = f'/appointments/{appointment.id}'
    link_base = '<appointments?page-number={0}&page-size={1}>; {2}'
    links = prepare_pagination_link(link_base, pagination,appointments_number)
    response.headers["Link"] = links
    return appointments
