from uuid import UUID
from typing import Annotated, Sequence, Any

import src.databases.models.patients
from fastapi import APIRouter, status, Depends, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

import src.services.authentication as auth
from src.services.general import prepare_pagination_link, prepare_new_patient
import src.data_access_layer.patients as dal_pat
import src.data_access_layer.general as dal_gen
import src.models.patients as mod_pat
import src.models.general as mod_gen

router = APIRouter(tags=['patients'], dependencies=[Depends(auth.validate_token)])

AsyncSessionDep = Annotated[AsyncSession, Depends(dal_gen.get_relational_async_session)]


@router.patch('/verify/patients/{patient_id}', status_code=status.HTTP_200_OK, response_model=mod_pat.Patient)
async def verify_patient(patient_id: UUID, session: AsyncSessionDep) -> src.databases.models.patients.Patients:
    async with session.begin():
        patient_data_access = dal_pat.Patients(session)
        patient = await patient_data_access.update(patient_id, {'is_verified': True})
    if patient is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    else:
        return patient


@router.get('/patients', status_code=status.HTTP_200_OK, response_model=list[mod_pat.PatientLocation])
async def get_patients(session: AsyncSessionDep, pagination: mod_gen.pagination_dependency, response: Response)\
                        -> Sequence[src.databases.models.patients.Patients]:
    async with session.begin():
        data_access = dal_pat.Patients(session)
        patients, patients_number = await data_access.get_many(pagination)
    if not patients:
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT)
    for patient in patients:
        patient.location = f'/patients/{patient.id}'
    link_base = '<patients?page-number={0}&page-size={1}>; {2}'
    links = prepare_pagination_link(link_base, pagination, patients_number)
    response.headers['Link'] = links
    return patients


@router.post('/patients', status_code=status.HTTP_201_CREATED, response_model=mod_pat.PatientPassword)
async def add_patient(patient: mod_pat.Patient, session: AsyncSessionDep, response: Response) \
                      -> src.databases.models.patients.Patients:
    patient: dict[str, Any] = patient.model_dump()
    patient, password = prepare_new_patient(patient)
    async with session.begin():
        patient_data_access = dal_pat.Patients(session)
        try:
            new_patient = await patient_data_access.add(patient)
        except IntegrityError:
            raise HTTPException(status_code=400, detail='introduced data violate database constraints.')
    patient_id = new_patient.id
    response.headers['Location'] = f'/patients/{patient_id}'
    new_patient.password = password
    return new_patient
