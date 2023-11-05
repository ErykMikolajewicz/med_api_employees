from uuid import UUID
from datetime import datetime

from pydantic import BaseModel


class Appointment(BaseModel):
    employee_id: UUID
    start: datetime
    end: datetime
    patient_id: UUID
