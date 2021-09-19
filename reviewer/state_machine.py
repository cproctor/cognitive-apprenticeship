from common.state_machine import StateMachine
from django.contrib import messages
from django.conf import settings
from django.utils import timezone
from datetime import datetime, timedelta
import logging
from .models import Review

logger = logging.getLogger("cognitive_apprenticeship.analytics")

class ReviewStateMachine(StateMachine):
    """Handles Revision state transitions and their side effects.
    """
    states = Review.StatusChoices

    def get_state(self, rev):
        return rev.status

    def assigned_to_submitted(self, rev, old_state, new_state):
        self.log_state_transition(rev, old_state, new_state)
        msg = "Your review was submitted. Awaiting an editor decision."
        self.flash_authors(rev, msg, level=messages.SUCCESS)
        rev.status = new_state
        rev.date_submitted = timezone.now()
        rev.save()

    def assigned_to_expired(self, rev, old_state, new_state):
        self.log_state_transition(rev, old_state, new_state)
        msg = "Your assigned review expired. You may contact the editor to request an extension."
        self.flash_authors(rev, msg, level=messages.WARNING)
        rev.status = new_state
        rev.date_closed = timezone.now()
        rev.save()

    def assigned_to_withdrawn(self, rev, old_state, new_state):
        self.log_state_transition(rev, old_state, new_state)
        msg = "The manuscript you were assigned to review was withdrawn by its author."
        self.flash_authors(rev, msg)
        rev.status = new_state
        rev.date_closed = timezone.now()
        rev.save()

    def assigned_to_not_needed(self, rev, old_state, new_state):
        print("  > executing assigned_to_not_needed")
        self.log_state_transition(rev, old_state, new_state)
        msg = "The editor made a decision on this manuscript before your review was submitted"
        self.flash_authors(rev, msg)
        rev.status = new_state
        rev.date_closed = timezone.now()
        rev.save()

    def submitted_to_complete(self, rev, old_state, new_state):
        self.log_state_transition(rev, old_state, new_state)
        msg = "A manuscript you reviewed received an editorial decision."
        self.flash_authors(rev, msg)
        rev.status = new_state
        rev.save()

    def submitted_to_edit_requested(self, rev, old_state, new_state):
        self.log_state_transition(rev, old_state, new_state)
        msg = "The editor requested that you edit your review."
        self.flash_authors(rev, msg.format(rev.title))
        rev.status = new_state
        rev.date_due = timezone.now() + timedelta(days=settings.DAYS_TO_EDIT_REVIEW)
        rev.save()

    def expired_to_assigned(self, rev, old_state, new_state):
        self.log_state_transition(rev, old_state, new_state)
        msg = "The editor extended the deadline for an expired review."
        self.flash_authors(rev, msg)
        rev.status = new_state
        rev.date_due = timezone.now() + timedelta(days=settings.DAYS_ON_EXTENSION) 
        rev.date_complete = None
        rev.save()

    def edit_requested_to_submitted(self, rev, old_state, new_state):
        self.log_state_transition(rev, old_state, new_state)
        msg = "You resubmitted your review."
        self.flash_authors(rev, msg, level=messages.SUCCESS)
        rev.status = new_state
        rev.date_submitted = timezone.now()
        rev.save()

    def edit_requested_to_expired(self, rev, old_state, new_state):
        self.log_state_transition(rev, old_state, new_state)
        msg = "A review with edits requested has passed its deadline."
        self.flash_authors(rev, msg, level=messages.WARNING)
        rev.status = new_state
        rev.save()

    def log_state_transition(self, rev, old_state, new_state):
        msg = "Review {} transitioned from {} to {}".format(rev.id, old_state, new_state)
        logger.info(msg, extra={
            'event': 'state_transition',
            'old_state': old_state,
            'new_state': new_state,
            'model': 'Review',
            'user': self.request.user.username if self.request else None,
            'id': rev.id,
        })

    def flash_authors(self, rev, message, level=messages.INFO):
        "Sets a flash message if the current user is the reviewer"
        if self.request and self.request.user == rev.reviewer:
            messages.add_message(self.request, level, message)
            
    transitions = {
        states.ASSIGNED: {
            states.SUBMITTED: assigned_to_submitted,
            states.EXPIRED: assigned_to_expired,
            states.NOT_NEEDED: assigned_to_not_needed,
            states.WITHDRAWN: assigned_to_withdrawn,
        },
        states.SUBMITTED: {
            states.COMPLETE: submitted_to_complete,
            states.EDIT_REQUESTED: submitted_to_edit_requested,
        },
        states.EXPIRED: {
            states.ASSIGNED: expired_to_assigned,
        },
        states.EDIT_REQUESTED: {
            states.SUBMITTED,
            states.EXPIRED,
        },
    }

    
