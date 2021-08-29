from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.detail import DetailView
from author.models import Manuscript, Revision
from author.mixins import ManuscriptRevisionMixin

from .models import Review
from .mixins import ReviewerMixin

class ReviewerHome(ReviewerMixin, TemplateView):
    template_name = "reviewer/home.html"

    def get_context_data(self):
        c = super().get_context_data()
        u = self.request.user
        qs = u.reviews.filter(revision__manuscript__reviewers=u)
        c['reviews_assigned'] = qs.filter(status=Review.StatusChoices.ASSIGNED).all()
        closed_statuses = [
            Review.StatusChoices.EXPIRED,
            Review.StatusChoices.COMPLETE
        ]
        c['reviews_closed'] = qs.filter(status__in=closed_statuses).all()
        return 

class ShowManuscript(ReviewerMixin, DetailView):
    """Redirects to show the manuscript's last revision.
    """
    model = Manuscript

    def get_queryset(self):
        return Manuscript.objects.filter(reviewers=self.request.user)

    def get(self, request, *args, **kwargs):
        m = self.get_object()
        return redirect('show_revision', m.id, m.revisions.last().revision_number)
class ShowRevision(ReviewerMixin, ManuscriptRevisionMixin, DetailView):
    """Implements the main tab for a revision.
    """
    model = Revision
    template_name = "reviewer/revision_detail.html"

class ShowRevisionReviews(ReviewerMixin, DetailView):
    """Implements the reviews tab for a mixin."""

class ReviewRevision(ReviewerMixin, UpdateView):
    """Implements the review-authoring tab for a revision.
    """

