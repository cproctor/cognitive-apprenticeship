from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.detail import DetailView
from author.models import Manuscript, Revision
from author.mixins import ManuscriptRevisionMixin
from django.urls import reverse
from django.shortcuts import redirect
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.shortcuts import Http404

from .models import Review
from .mixins import ReviewerMixin, RevisionReviewMixin
from .forms import EditReviewForm
from .state_machine import ReviewStateMachine

class ReviewerHome(ReviewerMixin, TemplateView):
    template_name = "reviewer/home.html"

    def get_context_data(self):
        c = super().get_context_data()
        my_reviews = Review.objects.filter(reviewer=self.request.user)..all()
        for col, reviews in Review.in_kanban_columns(my_reviews).items():
            c[col.name] = reviews
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

class ShowRevision(ReviewerMixin, ManuscriptRevisionMixin, RevisionReviewMixin, DetailView):
    """Implements the main tab for a revision.
    """
    model = Revision
    template_name = "reviewer/manuscript_revision_detail.html"

class ShowReviews(ReviewerMixin, ManuscriptRevisionMixin, DetailView):
    """Implements the reviews tab."""
    template_name = "reviewer/reviews_detail.html"

class ShowReview(ReviewerMixin, ManuscriptRevisionMixin, RevisionReviewMixin, DetailView):
    """Implements the review tab."""
    template_name = "reviewer/review_detail.html"

    def get(self, request, *args, **kwargs):
        review = self.get_review()
        if review.revision.status == Revision.StatusChoices.PENDING and not review.text:
            m_id = self.get_revision().manuscript_id
            return redirect('reviewer:edit_review', m_id, self.get_revision().revision_number)
        else:
            return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        "Handles POST actions"
        review = self.get_review()
        sm = ReviewStateMachine(request)
        action = request.POST['action'].upper()
        if action == "SUBMIT":
            try:
                sm.transition(review, sm.states.SUBMITTED)
            except sm.IllegalTransition:
                return self.forbid_action("submit")
        else:
            return self.forbid_action(action)
        m_id = self.get_revision().manuscript_id
        return redirect('reviewer:show_review', m_id, self.get_revision().revision_number)

    def forbid_action(self, action):
        msg = "Action '{}' is not allowed.".format(action)
        messages.add_message(self.request, messages.WARNING, msg)
        return HttpResponseForbidden(msg)
        
class ReviewInstructions(ReviewerMixin, ManuscriptRevisionMixin, RevisionReviewMixin, TemplateView):
    """Implements the review instructions tab."""
    template_name = "reviewer/review_instructions.html"

class EditReview(ReviewerMixin, ManuscriptRevisionMixin, RevisionReviewMixin, UpdateView):
    """Implements the review-authoring tab for a revision.
    """
    model = Review
    form_class = EditReviewForm
    template_name = "reviewer/edit_review.html"

    def get_object(self):
        if self.get_revision().status != Revision.StatusChoices.PENDING:
            raise Http404()
        return self.get_review()

    def get_revision(self):
        try:
            return self.get_queryset().get(
                manuscript__id=self.kwargs['manuscript_pk'],
                revision_number=self.kwargs['revision_number']
            )
        except Revision.DoesNotExist:
            raise Http404("No such revision")

    def get_success_url(self):
        revision = self.get_revision()
        return reverse('reviewer:show_review', args=(revision.manuscript_id, revision.revision_number))

