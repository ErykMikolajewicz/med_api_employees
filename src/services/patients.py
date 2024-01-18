from sqlalchemy.ext.asyncio import AsyncSession

from src.data_access_layer.patients import Patients


def send_email_to_patient(patient_email, email_text):
    pass


def send_sms_to_patient(patient_number, sms_text):
    pass


def notify_patient_in_app(patient_id, notification_text):
    pass


async def notify_cancel_visit(patient_id, session: AsyncSession):
    async with session.begin():
        patient_dal = Patients(session)
        patient = await patient_dal.get(patient_id)
    if patient.email_verified:
        send_email_to_patient(patient.email, 'Twoja wizyta została odwołana.')
    if patient.telephone_verified:
        send_sms_to_patient(patient.telephone, 'Twoja wizyta została odwołana.')
    notify_patient_in_app(patient_id, 'Twoja wizyta została odwołana.')

