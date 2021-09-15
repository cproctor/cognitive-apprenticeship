from common.email import send_journal_email
from django.conf import settings
from django.urls import reverse

REVIEW_CREATED_MESSAGE = """Dear {}, 

You have been assigned to review a manuscript for the {}. The review is due {}. 
To write the review, please log in at {}."""

def notify_user_when_review_created(review):
    if review.reviewer.email:
        due_date = review.date_due.strftime("%B %-d, %-I:%M %p")
        send_journal_email(
            "You have been assigned as a reviewer",
            REVIEW_CREATED_MESSAGE.format(
                review.reviewer.first_name,
                settings.JOURNAL_NAME,
                due_date,
                settings.JOURNAL_EMAIL_BASE_URL + reverse('reviewer:home'),
            ),
            [review.reviewer.email],
        )
