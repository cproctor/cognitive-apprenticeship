from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.shortcuts import redirect
from django.conf import settings
from author.models import Manuscript, Revision
from reviewer.models import Review
from editor.forms import AssignReviewerForm
from datetime import datetime, timedelta

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

    def get_context_data(self, **kwargs):
        c = super().get_context_data(**kwargs)

        unsubmitted = []
        pending = []
        decided = []
        published = []

        qs = Manuscript.objects
        if 'q' in self.request.GET:
            qs = qs.filter(authors__username=self.request.GET['q'])
        qs = qs.count_reviews('num_reviews')
        qs = qs.count_reviews('num_complete_reviews', status=Review.StatusChoices.COMPLETE)

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
        for m in qs.all():
            r = m.revisions.last() # TODO Poor performance; prefetch
            bins[r.status].append(m)

        c['unsubmitted_manuscripts'] = unsubmitted
        c['pending_manuscripts'] = pending
        c['decided_manuscripts'] = decided
        c['published_manuscripts'] = published

        return c
        
class ShowEditorManuscript(EditorRoleRequiredMixin, DetailView):
    model = Manuscript
    template_name = 'editor/show_manuscript.html'
    http_method_names = ['get', 'post']

    def __init__(self, *args, **kwargs):
        super(*args, **kwargs)
        self.object = None

    def get_context_data(self, **kwargs):
        c = super().get_context_data(**kwargs)
        c['assign_reviewer_form'] = AssignReviewerForm(self.get_object())
        return c

    def post(self, request, *args, **kwargs):
        manuscript = self.get_object()
        context = self.get_context_data()
        action = request.POST['action'].upper()
        if action.upper() == 'ASSIGN_REVIEWER':
            form = AssignReviewerForm(manuscript, request.POST)
            if form.is_valid():
                user = form.cleaned_data['reviewer']
                manuscript.reviewers.add(user)
                if not Review.objects.filter(revision__manuscript=manuscript, reviewer=user).exists():
                    Review.objects.create(
                        reviewer=user,
                        revision=manuscript.revisions.last(),
                        status=Review.StatusChoices.ASSIGNED,
                        date_due=datetime.now() + timedelta(days=settings.DAYS_TO_REVIEW)
                    )
                return redirect('editor:show_manuscript', manuscript.id)
            else:
                context['assign_reviewer_form'] = form
                return render(request, self.template_name, context)
        elif action.upper() == 'REMOVE_REVIEWER':
            user = manuscript.reviewers.get(username=request.POST['username'])
            Review.objects.filter(revision__manuscript=manuscript, reviewer=user).delete()
            manuscript.reviewers.remove(user)
            return redirect('editor:show_manuscript', manuscript.id)

            


class ListEditorReviews(EditorRoleRequiredMixin, TemplateView):
    template_name = "editor/list_reviews.html"






