from datetime import datetime
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from tinymce.models import HTMLField
from common.models import NondeletedManager
from django.db.models import Q, Count
from enum import Enum, auto

class ManuscriptQuerySet(models.QuerySet):
    def count_reviews(self, name, **kwargs):
        "Annotates the query with a count of reviews, optionally filtered."
        filter_kwargs = {'revisions__reviews__' + k : v for k, v in kwargs.items()}
        agg = Count('revisions__reviews', filter=Q(**filter_kwargs))
        return self.annotate(**{name: agg})

class ManuscriptManager(models.Manager):
    "A manager which uses ManuscriptQuerySet and which filters out deleted"
    def get_queryset(self):
        return ManuscriptQuerySet(self.model, using=self._db).filter(deleted=False)

    def count_reviews(self, name, **kwargs):
        return self.get_queryset().count_reviews(name, **kwargs)

class Manuscript(models.Model):
    authors = models.ManyToManyField(User, through="author.ManuscriptAuthorship", related_name="manuscripts")
    reviewers = models.ManyToManyField(User, through="reviewer.ManuscriptReviewer", 
            related_name="reviewed_manuscripts")
    deleted = models.BooleanField(default=False)

    objects = ManuscriptManager()

    def __str__(self):
        return '"{}" by {} ({})'.format(self.short_title(), self.author_names(), self.status_message())

    def get_absolute_url(self):
        return reverse('author:show_manuscript', self.id)

    def has_unacknowledged_authors(self):
        return self.authors.filter(manuscriptauthorship__acknowledged=False).exists()

    def can_assign_reviewer(self):
        "Whether it is possible to assign a reviewer to this manuscript"
        return self.revisions.last().status == Revision.StatusChoices.PENDING

    def short_title(self):
        "Someday will appropriately shorten the title"
        return self.revisions.last().title

    def author_names(self):
        return self.format_names(self.authors.all())

    def reviewer_names(self):
        return self.format_names(self.reviewers.all())

    def format_names(self, users):
        authors = ["{} {}".format(u.first_name, u.last_name) for u in users]
        if len(authors) == 1:
            return authors[0]
        else:
            return ', '.join(authors[:-1]) + ' and ' + authors[-1]

    def status_message(self):
        return self.revisions.last().status_message()

    def kanban_column(self):
        return Revision.KANBAN_ASSIGNMENT[self.revisions.last().status]

    @classmethod
    def in_kanban_columns(self, manuscripts):
        return {col: [m for m in manuscripts if m.kanban_column() == col] for col in Revision.KanbanColumns}

class ManuscriptAuthorship(models.Model):
    manuscript = models.ForeignKey(Manuscript, on_delete=models.CASCADE,
        related_name="authorships")
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    acknowledged = models.BooleanField(default=False)

class Revision(models.Model):
    timeformat = "%A %B %-d, %Y at %-I:%M %p"

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
    revision_note = HTMLField(blank=True, null=True)
    text = HTMLField()
    editorial_review = HTMLField(blank=True, null=True)
    date_created = models.DateTimeField()
    date_submitted = models.DateTimeField(blank=True, null=True)
    date_decided = models.DateTimeField(blank=True, null=True)
    date_published = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=StatusChoices.choices,
            default=StatusChoices.UNSUBMITTED)

    def __str__(self):
        return '"{}" by {} (v{} {})'.format(
            self.title, 
            self.manuscript.author_names(), 
            self.revision_number,
            self.status_message(),
        )

    def get_absolute_url(self):
        return reverse('author:show_revision', args=[self.manuscript_id, self.revision_number])

    def status_message(self):
        if self.status in (self.StatusChoices.UNSUBMITTED, self.StatusChoices.WAITING_FOR_AUTHORS):
            verb = "created"
            ts = self.date_created
        elif self.status == self.StatusChoices.WITHDRAWN:
            verb = "withdrawn"
            ts  = self.date_decided
        elif self.status == self.StatusChoices.PENDING:
            verb = "submitted"
            ts = self.date_submitted
        elif self.status == self.StatusChoices.ACCEPT:
            verb = "accepted"
            ts = self.date_decided
        elif self.status == self.StatusChoices.MINOR_REVISION:
            verb = "minor revisions requested"
            ts = self.date_decided
        elif self.status == self.StatusChoices.MAJOR_REVISION:
            verb = "major revisions requested"
            ts = self.date_decided
        elif self.status == self.StatusChoices.REJECT:
            verb = "rejected"
            ts = self.date_decided
        elif self.status == self.StatusChoices.PUBLISHED:
            verb = "published"
            ts = self.date_published
        return "{} {}".format(verb.capitalize(), timezone.localtime(ts).strftime(self.timeformat))

    def status_message_for_reviewers(self):
        if self.status == self.StatusChoices.PENDING:
            return "Awaiting review"
        else:
            return str(self.status)

    def create_new_revision(self):
        if self.manuscript.has_unacknowledged_authors():
            status = Revision.StatusChoices.WAITING_FOR_AUTHORS
        else:
            status = Revision.StatusChoices.UNSUBMITTED
        return self.manuscript.revisions.create(
            title=self.title,
            text=self.text,
            revision_number=self.revision_number + 1,
            date_created=timezone.now(),
            status=status,
        )

    def can_submit(self):
        is_unsubmitted = (self.status == self.StatusChoices.UNSUBMITTED)
        has_revision_note_if_needed = self.revision_note or not self.has_prior_decision()
        return is_unsubmitted and has_revision_note_if_needed

    def has_reviews_underway(self):
        review_underway_states = ['SUBMITTED', 'COMPLETE', 'EDIT_REQUESTED']
        return self.reviews.filter(status__in=review_underway_states).count()

    def is_withdrawn(self):
        return self.status == self.StatusChoices.WITHDRAWN

    def can_withdraw(self):
        return (
            self.status == self.StatusChoices.PENDING and
            not self.has_reviews_underway()
        )
    def can_create_new_revision(self):
        valid_statuses = [
            self.StatusChoices.WITHDRAWN,
            self.StatusChoices.MINOR_REVISION,
            self.StatusChoices.MAJOR_REVISION,
        ]
        later_revisions = self.manuscript.revisions.filter(revision_number__gt=self.revision_number)
        return self.status in valid_statuses and not later_revisions.exists()

    def has_prior_decision(self):
        return self.manuscript.revisions.filter(
            revision_number__lt=self.revision_number,
            status__in=[
                self.StatusChoices.REJECT, 
                self.StatusChoices.MINOR_REVISION, 
                self.StatusChoices.MAJOR_REVISION,
                self.StatusChoices.ACCEPT, 
                self.StatusChoices.PUBLISHED, 
            ],
        ).exists()

    def can_edit(self):
        valid_statuses = [
            self.StatusChoices.UNSUBMITTED,
            self.StatusChoices.WAITING_FOR_AUTHORS,
        ]
        return self.status in valid_statuses

    def should_show_reviews_to_author(self):
        return self.kanban_column() in [
            self.KanbanColumns.DECIDED,
            self.KanbanColumns.PUBLISHED
        ]

    class KanbanColumns(Enum):
        IN_PREPARATION = auto()
        IN_SUBMISSION = auto()
        DECIDED = auto()
        PUBLISHED = auto()

    KANBAN_ASSIGNMENT = {
        StatusChoices.UNSUBMITTED:          KanbanColumns.IN_PREPARATION,
        StatusChoices.WAITING_FOR_AUTHORS:  KanbanColumns.IN_PREPARATION,
        StatusChoices.WITHDRAWN:            KanbanColumns.IN_PREPARATION,
        StatusChoices.PENDING:              KanbanColumns.IN_SUBMISSION,
        StatusChoices.ACCEPT:               KanbanColumns.DECIDED,
        StatusChoices.MINOR_REVISION:       KanbanColumns.DECIDED,
        StatusChoices.MAJOR_REVISION:       KanbanColumns.DECIDED,
        StatusChoices.REJECT:               KanbanColumns.DECIDED,
        StatusChoices.PUBLISHED:            KanbanColumns.PUBLISHED,
    }

    def kanban_column(self):
        return self.KANBAN_ASSIGNMENT[self.status]

    @classmethod
    def in_kanban_columns(self, revisions):
        return {col: [r for r in revisions if r.kanban_column() == col] for col in self.KanbanColumns}

