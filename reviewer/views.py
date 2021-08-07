from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView

from .models import Review

class ReviewerRoleRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            msg = "You must be logged in to view reviewer pages."
            messages.add_message(request, messages.WARNING, msg)
            return redirect('home_page')
        if not request.user.profile.is_reviewer:
            msg = "You are not registered as a reviewer."
            messages.add_message(request, messages.WARNING, msg)
            return redirect('home_page')
        return super().dispatch(request, *args, **kwargs)

class ReviewerHome(ReviewerRoleRequiredMixin, TemplateView):
    template_name = "reviewer/home.html"

    def get_context_data(self):
        u = self.request.user
        c = super().get_context_data()
        c['reviews_assigned'] = u.reviews.filter(status=Review.StatusChoices.ASSIGNED).all()
        closed_statuses = [
            Review.StatusChoices.EXPIRED,
            Review.StatusChoices.COMPLETE
        ]
        c['reviews_closed'] = u.reviews.filter(status__in=closed_statuses).all()

class ReviewManuscript(CreateView):
    model = Review
