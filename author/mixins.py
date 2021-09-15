from django.contrib import messages
from django.shortcuts import redirect
from .models import Revision

class AuthorMixin:
    def dispatch(self, request, *args, **kwargs):
        """Ensures that there is a currently logged-in user with author role. 
        Otherwise, redirects to home page with a flash message.
        """
        if not request.user.is_authenticated:
            msg = "You must be logged in to view authors pages."
            messages.add_message(request, messages.WARNING, msg)
            return redirect('public:home_page')
        if not request.user.profile.is_author:
            msg = "You are not registered as an author."
            messages.add_message(request, messages.WARNING, msg)
            return redirect('public:home_page')
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        """Ensures that the revision is part of a Manuscript with the current
        user as author. Assumes that the view's Model is Revision. 
        """
        return Revision.objects.filter(manuscript__authors=self.request.user)

class ManuscriptRevisionMixin:
    """A mixin which overrides `get_object` to look up a revision nested within
    a manuscript. Populates `manuscript` and `revision` in template context.
    Expects `manuscript_pk` and `revision_number` in url kwargs.
    """
    def get_object(self, queryset=None):
        "Looks up a revision by manuscript id and revision_number."
        qs = queryset or self.get_queryset()
        try:
            qs = Revision.objects.filter(
                manuscript__id=self.kwargs['manuscript_pk'],
                revision_number=self.kwargs['revision_number']
            )
            return qs.get()
        except Revision.DoesNotExist:
            raise Http404("No such revision")

    def get_context_data(self, *args, **kwargs):
        "Populates `manuscript` and `revision` in template context."
        ctx = super().get_context_data(*args, **kwargs)
        revision = self.get_object()
        ctx['revision'] = revision
        ctx['manuscript'] = revision.manuscript
        return ctx

