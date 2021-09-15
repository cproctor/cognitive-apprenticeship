from common.email import send_journal_email
from django.conf import settings
from django.urls import reverse

UNSUBMITTED_TO_WAITING_FOR_AUTHORS_EMAIL = """Dear {},

You were listed as a co-author of the manuscript "{}." If you agree to be a co-author, 
please log in to {} and click "Acknowledge authorship." Thanks!"""
    
UNSUBMITTED_TO_PENDING_EMAIL = """Dear {}, 

Your manuscript "{}" has been submitted and reviewers have been assigned.
You will be notified once the reviews have been received. Thanks!
"""

PENDING_TO_DECIDED_EMAIL = """Dear {}, 

The reviews are in for your manuscript "{}" and a decision has been
returned. Please log in to {} to read the reviews and take any necessary
actions. Thanks!
"""

def notify_user_revision_transitioned_from_unsubmitted_to_waiting_for_authors(revision):
    for authorship in revision.manuscript.authorships.filter(acknowledged=False).all():
        author = authorship.author
        if author.email:
            send_journal_email(
                "You were listed as a co-author",
                UNSUBMITTED_TO_WAITING_FOR_AUTHORS_EMAIL.format(
                    author.first_name, 
                    revision.title,
                    settings.JOURNAL_EMAIL_BASE_URL + reverse(
                        'author:show_revision',
                        args=(revision.manuscript.id, revision.revision_number)
                    ),
                ),
                [author.email],
            )
    
def notify_user_revision_transitioned_from_unsubmitted_to_pending(revision):
    for author in revision.manuscript.authors.all():
        if author.email:
            send_journal_email(
                "Your manuscript was submitted",
                UNSUBMITTED_TO_PENDING_EMAIL.format(
                    author.first_name, 
                    revision.title,
                ),
                [author.email],
            )
    
def notify_user_revision_transitioned_from_pending_to_decided(revision):
    for author in revision.manuscript.authors.all():
        if author.email:
            send_journal_email(
                "Your manuscript has a decision",
                PENDING_TO_DECIDED_EMAIL.format(
                    author.first_name, 
                    revision.title,
                    settings.JOURNAL_EMAIL_BASE_URL + reverse('author:home'),
                ),
                [author.email],
            )
    
