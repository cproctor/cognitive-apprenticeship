from author.models import Revision
from .models import Review
from django.contrib import messages
from django.shortcuts import redirect
from django.http import Http404

class ReviewerMixin:
    def dispatch(self, request, *args, **kwargs):
        """Ensures that there is a currently logged-in user with reviewer role. 
        Otherwise, redirects to home page with a flash message.
        """
        if not request.user.is_authenticated:
            msg = "You must be logged in to view reviewer pages."
            messages.add_message(request, messages.WARNING, msg)
            return redirect('public:home_page')
        if not request.user.profile.is_reviewer:
            msg = "You are not registered as a reviewer."
            messages.add_message(request, messages.WARNING, msg)
            return redirect('public:home_page')
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        """Ensures that the revision is part of a Manuscript with the current
        user as reviewer. Assumes that the view's Model is Revision. 
        """
        return Revision.objects.filter(manuscript__reviewers=self.request.user)

class RevisionReviewMixin:
    def get_revision(self):
        "Looks up a revision by manuscript id and revision_number."
        try:
            qs = Revision.objects.filter(
                manuscript__id=self.kwargs['manuscript_pk'],
                revision_number=self.kwargs['revision_number']
            )
            return qs.get()
        except Revision.DoesNotExist:
            raise Http404("No such revision")

    def get_review(self):
        """Returns the review.
        """
        revision = self.get_revision()
        try:
            return revision.reviews.get(reviewer=self.request.user)
        except Review.DoesNotExist:
            return None

    def get_context_data(self, *args, **kwargs):
        """Populates shared context data.
        """
        c = super().get_context_data(*args, **kwargs)
        review = self.get_review()
        c['review'] = review
        c['review_deadline'] = review.date_due if review else None
        #c['show_review_tab'] = review.should_show
        return c
