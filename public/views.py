from django.views.generic.base import TemplateView

class HomePage(TemplateView):
    template_name = "public/home_page.html"

    def get_context_data(self):
        return {
          'articles': []
        }

class AboutPage(TemplateView):
    pass
