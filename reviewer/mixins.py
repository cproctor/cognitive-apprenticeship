from author.models import Revision
from django.contrib import messages
from django.shortcuts import redirect

class ReviewerMixin:
    def dispatch(self, request, *args, **kwargs):
        """Ensures that there is a currently logged-in user with reviewer role. 
        Otherwise, redirects to home page with a flash message.
        """
        if not request.user.is_authenticated:
            msg = "You must be logged in to view reviewer pages."
            messages.add_message(request, messages.WARNING, msg)
            return redirect('home_page')
        if not request.user.profile.is_reviewer:
            msg = "You are not registered as a reviewer."
            messages.add_message(request, messages.WARNING, msg)
            return redirect('home_page')
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        """Ensures that the revision is part of a Manuscript with the current
        user as reviewer. Assumes that the view's Model is Revision. 
        """
        return Revision.objects.filter(manuscript__reviewers=self.request.user)

