from django.shortcuts import render
from django.views.generic.base import TemplateView
from django.conf import settings
from common.email import send_journal_email

class TestEmail(TemplateView):
    template_name = "common/email_test.html"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['index'] = self.kwargs['index']
        return context

    def get(self, *args, **kwargs):
        index = self.kwargs['index']
        send_journal_email(
            f"Email test {index}",
            f"This is a test.",
            [addr for name, addr in settings.ADMINS]
        )
        return super().get(*args, **kwargs)

