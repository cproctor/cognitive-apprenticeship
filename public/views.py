from django.views.generic.base import TemplateView
from editor.models import JournalIssue
from django.conf import settings

class HomePage(TemplateView):
    template_name = "public/home_page.html"

    def get_context_data(self):
        return {
            'issues': JournalIssue.objects.filter(published=True).all(),
            'editor_names': settings.EDITOR_NAMES,
        }

class AboutPage(TemplateView):
    pass
