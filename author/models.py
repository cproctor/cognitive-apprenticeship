from django.db import models
from django.contrib.auth.models import User
from tinymce.models import HTMLField
from common.models import NondeletedManager

class Manuscript(models.Model):
    authors = models.ManyToManyField(User, through="author.ManuscriptAuthorship", related_name="manuscripts")
    reviewers = models.ManyToManyField(User, through="reviewer.ManuscriptReviewer", 
            related_name="reviewed_manuscripts")
    deleted = models.BooleanField(default=False)

    objects = NondeletedManager()

    def has_unacknowledged_authors(self):
        return self.authors.filter(manuscriptauthorship__acknowledged=False).exists()

    def short_title(self):
        "Someday will appropriately shorten the title"
        return self.revisions.last().title

    def author_names(self):
        authors = ["{} {}".format(a.first_name, a.last_name) for a in self.authors.all()]
        if len(authors) == 1:
            return authors[0]
        else:
            return ', '.join(authors[:-1]) + 'and ' + authors[-1]

class ManuscriptAuthorship(models.Model):
    manuscript = models.ForeignKey(Manuscript, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    acknowledged = models.BooleanField(default=False)

class Revision(models.Model):
    timeformat = "%A %B %-m, %Y at %-I:%M %p"

    class StatusChoices(models.TextChoices):
        UNSUBMITTED = 'UNSUBMITTED', 'Unsubmitted'
        WAITING_FOR_AUTHORS = 'WAITING_FOR_AUTHORS', 'Waiting for authors'
        WITHDRAWN = 'WITHDRAWN', 'Withdrawn'
        PENDING = 'PENDING', 'Pending'
        ACCEPT = 'ACCEPT', 'Accept'
        MINOR_REVISION = 'MINOR', 'Minor revision'
        MAJOR_REVISION = 'MAJOR', 'Major revision'
        REJECT = 'REJECT', 'Reject'
        PUBLISHED = 'PUBLISHED', 'Published'

    manuscript = models.ForeignKey(Manuscript, on_delete=models.CASCADE,
            related_name="revisions")
    title = models.CharField(max_length=200)
    revision_number = models.IntegerField()
    revision_note = models.TextField(blank=True, null=True)
    text = HTMLField()
    date_created = models.DateTimeField()
    date_submitted = models.DateTimeField(blank=True, null=True)
    date_decided = models.DateTimeField(blank=True, null=True)
    date_published = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=StatusChoices.choices,
            default=StatusChoices.PENDING)

    def status_message(self):
        if self.status in (self.StatusChoices.UNSUBMITTED, self.StatusChoices.WAITING_FOR_AUTHORS):
            verb = "created".format(self.date_created.strftime(self.timeformat))
            ts = self.date_created
        elif self.status == self.StatusChoices.WITHDRAWN:
            verb = "withdrawn"
            ts  = self.date_decided
        elif self.status == self.StatusChoices.PENDING:
            verb = "submitted"
            ts = self.date_submitted
        elif self.status == self.StatusChoices.PUBLISHED:
            verb = "published"
            ts = self.date_published
        else:
            verb = "decision received"
            ts = self.date_decided
        return "{} ({} {})".format(self.status, verb, ts.strftime(self.timeformat))

    def can_submit(self):
        return self.status == self.StatusChoices.UNSUBMITTED
    def can_withdraw(self):
        return self.status == self.StatusChoices.PENDING
    def can_create_new_revision(self):
        return self.status in [
            self.StatusChoices.WITHDRAWN,
            self.StatusChoices.MINOR_REVISION,
            self.StatusChoices.MAJOR_REVISION,
        ]



