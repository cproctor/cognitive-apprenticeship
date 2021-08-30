from django.db import models
from django.contrib.auth.models import User

class ReviewManager(models.Manager):
    def for_manuscript(self, manuscript):
        return self.get_queryset().filter(revision__manuscript=manuscript)

class Review(models.Model):
    class StatusChoices(models.TextChoices):
        ASSIGNED = 'ASSIGNED', 'Assigned'
        COMPLETE = 'COMPLETE', 'Complete'
        EXPIRED = 'EXPIRED', 'Expired'
        WITHDRAWN = 'WITHDRAWN', 'Manuscript was withdrawn'
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
    date_due = models.DateTimeField()
    date_submitted = models.DateTimeField(blank=True, null=True)
    editor_feedback = models.TextField(blank=True, null=True)

    objects = ReviewManager()

    def __str__(self):
        return 'Review of "{}" v{} assigned to {} ({})'.format(
            self.revision.title,
            self.revision.revision_number,
            self.reviewer.username,
            self.status
        )

class ManuscriptReviewer(models.Model):
    manuscript = models.ForeignKey('author.Manuscript', on_delete=models.CASCADE)
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE)
