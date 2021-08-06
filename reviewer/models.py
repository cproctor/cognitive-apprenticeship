from django.db import models
from django.contrib.auth.models import User

class Review(models.Model):
    class StatusChoices(models.TextChoices):
        ASSIGNED = 'ASSIGNED', 'Assigned'
        COMPLETE = 'COMPLETE', 'Complete'
        EXPIRED = 'EXPIRED', 'Expired'
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
            choices=RecommendationChoices.choices, null=True)
    date_due = models.DateTimeField()
    date_submitted = models.DateTimeField()

class ManuscriptReviewer(models.Model):
    manuscript = models.ForeignKey('author.Manuscript', on_delete=models.CASCADE)
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE)
