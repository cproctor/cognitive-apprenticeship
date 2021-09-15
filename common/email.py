from django.core.mail import send_mail
from django.conf import settings
import logging
from datetime import datetime

logger = logging.getLogger("cognitive_apprenticeship.email")

def send_journal_email(subject, body, recipients):
    """Sends an email and logs the result.
    This function should be used to send all email throughout the application so
    that it can be managed centrally.
    """
    msg = "Email to {}: {}".format(recipients, subject)
    logger.info(msg, extra={
        'recipients': recipients,
        'sender': settings.JOURNAL_EMAIL_SENDER,
        'subject': subject,
        'body': body,
        'timestamp': datetime.now(),
        'sent': settings.SEND_JOURNAL_EMAIL,
    })
    if settings.SEND_JOURNAL_EMAIL:
        send_mail(
            settings.JOURNAL_EMAIL_SUBJECT_PREFIX + subject,
            body, 
            settings.JOURNAL_EMAIL_SENDER, 
            recipients,
        )
