from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView

from .models import Review

class ReviewerHome(TemplateView):
    pass

class ReviewManuscript(CreateView):
    model = Review
