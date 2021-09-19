from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from enum import Enum, auto

class ReviewManager(models.Manager):
    def for_manuscript(self, manuscript):
        return self.get_queryset().filter(revision__manuscript=manuscript)

class Review(models.Model):
    class StatusChoices(models.TextChoices):
        ASSIGNED = 'ASSIGNED', 'Assigned'
        SUBMITTED = 'SUBMITTED', 'Submitted'
        COMPLETE = 'COMPLETE', 'Complete'
        EXPIRED = 'EXPIRED', 'Expired'
        WITHDRAWN = 'WITHDRAWN', 'Manuscript was withdrawn'
        NOT_NEEDED = 'NOT_NEEDED', "A decision was reached before this review was submitted"
        EDIT_REQUESTED = 'EDIT_REQUESTED', 'Editing of review requested'
    class RecommendationChoices(models.TextChoices):
        ACCEPT = 'ACCEPT', 'Accept'
        MINOR_REVISION = 'MINOR', 'Minor revision'
        MAJOR_REVISION = 'MAJOR', 'Major revision'
        REJECT = 'REJECT', 'Reject'
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    revision = models.ForeignKey('author.Revision', on_delete=models.CASCADE,
            related_name='reviews')
    text = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.ASSIGNED)
    recommendation = models.CharField(max_length=20,
            choices=RecommendationChoices.choices, blank=True, null=True)
    date_due = models.DateTimeField(blank=True, null=True)
    date_submitted = models.DateTimeField(blank=True, null=True)
    date_closed = models.DateTimeField(blank=True, null=True)
    editor_feedback = models.TextField(blank=True, null=True)

    objects = ReviewManager()

    def __str__(self):
        return 'Review of "{}" v{} assigned to {} ({})'.format(
            self.revision.title,
            self.revision.revision_number,
            self.reviewer.username,
            self.status
        )

    def is_expired(self):
        return self.status == self.StatusChoices.EXPIRED

    def is_assigned(self):
        return self.status in [
            self.StatusChoices.ASSIGNED,
            self.StatusChoices.EDIT_REQUESTED,
        ]

    def is_submitted(self):
        return self.status == self.StatusChoices.SUBMITTED

    def get_absolute_url(self):
        return reverse('reviewer:show_review', 
                args=(self.revision.manuscript_id, self.revision.revision_number))
            
    def can_submit(self):
        return self.status in [
            self.StatusChoices.ASSIGNED,
            self.StatusChoices.EDIT_REQUESTED,
        ]

    class KanbanColumns(Enum):
        ASSIGNED = auto()
        SUBMITTED = auto()
        COMPLETE = auto()
        
    KANBAN_ASSIGNMENT = {
        StatusChoices.ASSIGNED:         KanbanColumns.ASSIGNED,
        StatusChoices.EDIT_REQUESTED:   KanbanColumns.ASSIGNED,
        StatusChoices.WITHDRAWN:        KanbanColumns.ASSIGNED,
        StatusChoices.EXPIRED:          KanbanColumns.ASSIGNED,
        StatusChoices.SUBMITTED:        KanbanColumns.SUBMITTED,
        StatusChoices.NOT_NEEDED:       KanbanColumns.COMPLETE,
        StatusChoices.COMPLETE:         KanbanColumns.COMPLETE,
    }

    def kanban_column(self):
        return self.KANBAN_ASSIGNMENT[self.status]

    @classmethod
    def in_kanban_columns(self, reviews):
        return {col: [r for r in reviews if r.kanban_column() == col] for col in self.KanbanColumns}

class ManuscriptReviewer(models.Model):
    manuscript = models.ForeignKey('author.Manuscript', on_delete=models.CASCADE)
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE)
