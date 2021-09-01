from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.detail import DetailView
from author.models import Manuscript, Revision
from author.mixins import ManuscriptRevisionMixin
from django.shortcuts import redirect

from .models import Review
from .mixins import ReviewerMixin, RevisionReviewMixin
from .forms import EditReviewForm

class ReviewerHome(ReviewerMixin, TemplateView):
    template_name = "reviewer/home.html"

    def get_context_data(self):
        c = super().get_context_data()
        my_reviews = Review.objects.filter(reviewer=self.request.user)

        assigned_statuses = [
            Review.StatusChoices.ASSIGNED,
            Review.StatusChoices.EDIT_REQUESTED,
        ]
        c['reviews_assigned'] = (my_reviews
            .filter(status__in=assigned_statuses)
            .filter(revision__status=Revision.StatusChoices.PENDING)
            .all()
        )
        closed_statuses = [
            Review.StatusChoices.EXPIRED,
            Review.StatusChoices.WITHDRAWN,
        ]
        c['reviews_closed'] = my_reviews.filter(status__in=closed_statuses).all()
        c['reviews_complete'] = my_reviews.filter(status=Review.StatusChoices.COMPLETE).all()
        return c

class ShowManuscript(ReviewerMixin, DetailView):
    """Redirects to show the manuscript's last revision.
    """
    model = Manuscript

    def get_queryset(self):
        return Manuscript.objects.filter(reviewers=self.request.user)

    def get(self, request, *args, **kwargs):
        m = self.get_object()
        return redirect('reviewer:show_revision', m.id, m.revisions.last().revision_number)

class ShowRevision(ReviewerMixin, ManuscriptRevisionMixin, DetailView):
    """Implements the main tab for a revision.
    """
    model = Revision
    template_name = "reviewer/manuscript_revision_detail.html"

class ShowReviews(ReviewerMixin, ManuscriptRevisionMixin, DetailView):
    """Implements the reviews tab."""
    template_name = "reviewer/reviews_detail.html"

class ShowReview(ReviewerMixin, ManuscriptRevisionMixin, DetailView):
    """Implements the review tab."""
    template_name = "reviewer/review_detail.html"

class ShowReviewInstructions(ReviewerMixin, ManuscriptRevisionMixin, TemplateView):
    """Implements the review instructions tab."""
    template_name = "reviewer/review_instructions.html"

class EditReview(ReviewerMixin, UpdateView):
    """Implements the review-authoring tab for a revision.
    """
    model = Review
    form_class = EditReviewForm
    template_name = "reviewer/edit_review.html"

    def get_object(self):
        return self.get_revision().reviews.get(reviewer=self.request.user)

    def get_context_data(self, *args, **kwargs):
        "Populates `manuscript` and `revision` in template context."
        ctx = super().get_context_data(*args, **kwargs)
        revision = self.get_revision()
        ctx['revision'] = revision
        ctx['manuscript'] = revision.manuscript
        return ctx
