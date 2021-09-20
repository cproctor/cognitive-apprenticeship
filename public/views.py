from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from editor.models import JournalIssue
from django.conf import settings

class PublicContextMixin:
    def get_context_data(self, *args, **kwargs):
        c = super().get_context_data(*args, **kwargs)
        c['issues'] = JournalIssue.objects.filter(published=True).all()
        c['editor_names'] = settings.EDITOR_NAMES
        return c

class HomePage(PublicContextMixin, TemplateView):
    template_name = "public/home_page.html"

class ShowIssue(PublicContextMixin, DetailView):
    model = JournalIssue
    template_name = "public/issue_detail.html"
    context_object_name = "issue"

    def get_queryset(self):
        return JournalIssue.objects.filter(published=True)

class AboutPage(TemplateView):
    pass
