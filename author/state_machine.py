from common.state_machine import StateMachine
from django.contrib import messages
from django.conf import settings
from datetime import datetime, timedelta
import logging
from .models import Revision
from reviewer.models import Review
from reviewer.state_machine import ReviewStateMachine

logger = logging.getLogger("cognitive_apprenticeship.analytics")

class RevisionStateMachine(StateMachine):
    """Handles Revision state transitions and their side effects.
    """
    states = Revision.StatusChoices

    def get_state(self, rev):
        return rev.status

    def unsubmitted_to_waiting_for_authors(self, rev, old_state, new_state):
        self.log_state_transition(rev, old_state, new_state)
        rev.status = self.states.WAITING_FOR_AUTHORS
        rev.save()
            
    def unsubmitted_to_pending(self, rev, old_state, new_state):
        self.log_state_transition(rev, old_state, new_state)
        msg = '"{}" has been submitted. You will be notified once reviewers provide feedback.'
        self.flash_authors(rev, msg.format(rev.title))
        rev.status = new_state
        rev.date_submitted = datetime.now()
        rev.save()
        for reviewer in rev.manuscript.reviewers.all():
            if not rev.reviews.filter(reviewer=reviewer).exists():
                rev.reviews.create(
                    reviewer=reviewer,
                    date_due=datetime.now() + timedelta(days=settings.DAYS_TO_REVIEW)
                )

    def waiting_for_authors_to_unsubmitted(self, rev, old_state, new_state):
        self.log_state_transition(rev, old_state, new_state)
        self.flash_authors(rev, "All authors have now acknowledged authorship of {}.")
        rev.status = new_state
        rev.save()

    def pending_to_withdrawn(self, rev, old_state, new_state):
        self.log_state_transition(rev, old_state, new_state)
        self.flash_authors(rev, "{} has been withdrawn and will not be reviewed.".format(rev.title))
        rev.status = new_state
        rev.date_decided = datetime.now()
        rev.save()
        review_state_machine = ReviewStateMachine()
        for review in rev.reviews.filter(status=Review.StatusChoices.ASSIGNED).all():
            review_state_machine.transition(review, Review.StatusChoices.WITHDRAWN)

    def pending_to_accept(self, rev, old_state, new_state):
        self._decision_transition(rev, old_state, new_state)

    def pending_to_minor_revision(self, rev, old_state, new_state):
        self._decision_transition(rev, old_state, new_state)

    def pending_to_major_revision(self, rev, old_state, new_state):
        self._decision_transition(rev, old_state, new_state)

    def pending_to_reject(self, rev, old_state, new_state):
        self._decision_transition(rev, old_state, new_state)

    def accept_to_published(self, rev, old_state, new_state):
        self.log_state_transition(rev, old_state, new_state)
        self.flash_authors("{} has been published!".format(rev.title))
        rev.status = new_state
        rev.date_published = datetime.now()
        rev.save()

    def _decision_transition(self, rev, old_state, new_state):
        self.log_state_transition(rev, old_state, new_state)
        self.flash_authors("{} has reviews and a decision.".format(rev.title))
        rev.status = new_state
        rev.date_decided = datetime.now()
        rev.save()

    def log_state_transition(self, rev, old_state, new_state):
        msg = "Revision {} transitioned from {} to {}".format(rev.id, old_state, new_state)
        logger.info(msg, extra={
            'event': 'state_transition',
            'old_state': old_state,
            'new_state': new_state,
            'model': 'Revision',
            'user': self.request.user.username if self.request else None,
            'id': rev.id,
        })

    def flash_authors(self, rev, message, level=messages.INFO):
        "Sets a flash message if the current user is an author of the revision"
        if self.request and self.request.user in rev.manuscript.authors.all():
            messages.add_message(self.request, level, message)
            
    transitions = {
        states.UNSUBMITTED: {
            states.WAITING_FOR_AUTHORS: unsubmitted_to_waiting_for_authors,
            states.PENDING: unsubmitted_to_pending,
        },
        states.WAITING_FOR_AUTHORS: {
            states.UNSUBMITTED: waiting_for_authors_to_unsubmitted,
        },
        states.PENDING: {
            states.WITHDRAWN: pending_to_withdrawn,
            states.ACCEPT: pending_to_accept,
            states.MINOR_REVISION: pending_to_minor_revision,
            states.MAJOR_REVISION: pending_to_major_revision,
            states.REJECT: pending_to_reject,
        },
        states.ACCEPT: {
            states.PUBLISHED: accept_to_published,
        }
    }

    
