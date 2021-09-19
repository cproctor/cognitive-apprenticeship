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

    VISIBLE_REVISION_STATUSES = [
        Revision.StatusChoices.WITHDRAWN,
        Revision.StatusChoices.PENDING,
        Revision.StatusChoices.ACCEPT,
        Revision.StatusChoices.MINOR_REVISION,
        Revision.StatusChoices.MAJOR_REVISION,
        Revision.StatusChoices.REJECT,
        Revision.StatusChoices.PUBLISHED,
    ]

    def get_queryset(self):
        """Ensures that the revision is part of a Manuscript with the current
        user as reviewer. Assumes that the view's Model is Revision. 
        """
        return Revision.objects.filter(
            manuscript__reviewers=self.request.user,
            status__in=self.VISIBLE_REVISION_STATUSES,
        )

    def get_context_data(self, *args, **kwargs):
        c = super().get_context_data(*args, **kwargs) 
        try:
            c['visible_revisions'] = self.get_queryset().filter(
                manuscript_id=self.kwargs['manuscript_pk']
            )
        except KeyError:
            pass
        return c

class RevisionReviewMixin:
    def get_review(self):
        try:
            return Review.objects.get(
                revision__manuscript_id=self.kwargs['manuscript_pk'],
                revision__revision_number=self.kwargs['revision_number'],
                reviewer=self.request.user,
            )
        except Review.DoesNotExist:
            raise Http404()

    def get_context_data(self, *args, **kwargs):
        c = super().get_context_data(*args, **kwargs)
        review = self.get_review()
        c['review'] = review
        c['review_deadline'] = review.date_due if review else None
        return c
