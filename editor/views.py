from django.views.generic.base import TemplateView
from author.models import Manuscript, Revision
from reviewer.models import Review

class EditorRoleRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            msg = "You must be logged in to view editor pages."
            messages.add_message(request, messages.WARNING, msg)
            return redirect('home_page')
        if not request.user.profile.is_editor:
            msg = "You are not registered as an editor."
            messages.add_message(request, messages.WARNING, msg)
            return redirect('home_page')
        return super().dispatch(request, *args, **kwargs)

class EditorHome(EditorRoleRequiredMixin, TemplateView):
    template_name = "editor/home.html"

class ListEditorManuscripts(EditorRoleRequiredMixin, TemplateView):
    template_name = "editor/list_manuscripts.html"

    def get_context_data(self):
        c = super().get_context_data()

        unsubmitted = []
        pending = []
        decided = []
        published = []
        # Here add kwarg
        if 'q' in self.request.GET:
            manuscripts = Manuscript.objects.filter(author__username=self.request.GET['q'])
        else: 
            manuscripts = Manuscript.objects.all()

        bins = {
            Revision.StatusChoices.UNSUBMITTED: unsubmitted,
            Revision.StatusChoices.WAITING_FOR_AUTHORS: unsubmitted,
            Revision.StatusChoices.WITHDRAWN: unsubmitted,
            Revision.StatusChoices.PENDING: pending,
            Revision.StatusChoices.ACCEPT: decided,
            Revision.StatusChoices.MAJOR_REVISION: decided,
            Revision.StatusChoices.REJECT: decided,
            Revision.StatusChoices.PUBLISHED: published,
        }
        for m in manuscripts:
            r = m.revisions.last() # TODO Poor performance; prefetch
            bins[r.status].append(m)

        c['unsubmitted_manuscripts'] = unsubmitted
        c['pending_manuscripts'] = pending
        c['decided_manuscripts'] = decided
        c['published_manuscripts'] = published

        return c
        

class ListEditorReviews(EditorRoleRequiredMixin, TemplateView):
    template_name = "editor/list_reviews.html"
