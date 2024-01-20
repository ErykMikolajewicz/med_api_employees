from dataclasses import dataclass


@dataclass
class CancelVisit:
    email_subject: str = 'Cancellation of visit {visit_date:%Y-%m-%d %H:%M:%S}'
    email_body: str = """
    We regret to inform you that your visit on {visit_date:%Y-%m-%d %H:%M:%S} has been canceled.
    We apologize for the difficulties.

    Best regards,
    MedApp team
    """
