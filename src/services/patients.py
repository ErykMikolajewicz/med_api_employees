import os
import json
from datetime import datetime
from email.mime.text import MIMEText

from sqlalchemy.ext.asyncio import AsyncSession
import aiosmtplib

from src.data_access_layer.patients import Patients
from src.texts.patients import CancelVisit


MED_APP_EMAIL_SECRETS_FILE = os.environ['MED_APP_EMAIL_SECRETS_FILE']
with open(MED_APP_EMAIL_SECRETS_FILE, 'r') as file:
    med_app_email_secrets = json.load(file)


async def send_email_to_patient(patient_email, med_app_email, password, subject, body):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = med_app_email
    msg['To'] = patient_email
    async with aiosmtplib.SMTP(hostname='smtp.gmail.com', port=465) as email_connection:
        await email_connection.login(med_app_email, password)
        await email_connection.sendmail(med_app_email, patient_email, msg.as_string())


def send_sms_to_patient(patient_number, sms_text):
    pass


def notify_patient_in_app(patient_id, notification_text):
    pass


async def notify_cancel_visit(patient_id, visit_start: datetime, session: AsyncSession):
    async with session.begin():
        patient_dal = Patients(session)
        patient = await patient_dal.get(patient_id)
    if patient.email_verified:
        med_app_email = med_app_email_secrets['email']
        med_app_password = med_app_email_secrets['password']

        email_subject = CancelVisit.email_subject
        email_subject.format(visit_date=visit_start)

        email_body = CancelVisit.email_body
        email_body.format(visit_date=visit_start)

        await send_email_to_patient(patient.email, med_app_email, med_app_password, email_subject, email_body)
    if patient.telephone_verified:
        send_sms_to_patient(patient.telephone, 'Twoja wizyta została odwołana.')
    notify_patient_in_app(patient_id, 'Twoja wizyta została odwołana.')
