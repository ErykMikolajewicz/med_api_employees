from uuid import UUID
from typing import Annotated, Sequence

from fastapi import APIRouter, status, Depends, HTTPException

import src.authentication.token as auth
import src.data_access_layer.patients as dal_pat
import src.data_access_layer.general as dal_gen
import src.models.patients as mod_pat
import src.models.general as mod_gen
import src.databases.models as db_mod

router = APIRouter(tags=['patients'], dependencies=[Depends(auth.validate_token)])

AsyncSessionDep = Annotated[dal_gen.db_rel.AsyncSession, Depends(dal_gen.get_relational_async_session)]


@router.patch("/verify/patients/{patient_id}", status_code=status.HTTP_200_OK)
async def verify_patient(patient_id: UUID, session: AsyncSessionDep) -> mod_pat.Patient:
    async with session.begin():
        raise NotImplementedError


@router.get("/patients", status_code=status.HTTP_200_OK, response_model=list[mod_pat.Patient])
async def get_patients(session: AsyncSessionDep, pagination: tuple[int, int] = Depends(mod_gen.pagination))\
                       -> Sequence[db_mod.Patients]:
    async with session.begin():
        patient_data_access = dal_pat.Patients(session)
        results = await patient_data_access.get_many(pagination)
    if not results:
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT)
    return results
