from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, FormView
from django.shortcuts import redirect
from django.urls import reverse
from django.conf import settings
from author.models import Manuscript, Revision
from author.mixins import ManuscriptRevisionMixin
from reviewer.models import Review
from editor.forms import AssignReviewerForm
from datetime import datetime, timedelta
from .models import JournalIssue
from .forms import NewJournalIssueForm, EditJournalIssueForm
from reviewer.email import notify_user_when_review_created

class EditorRoleRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            msg = "You must be logged in to view editor pages."
            messages.add_message(request, messages.WARNING, msg)
            return redirect('public:home_page')
        if not request.user.profile.is_editor:
            msg = "You are not registered as an editor."
            messages.add_message(request, messages.WARNING, msg)
            return redirect('public:home_page')
        return super().dispatch(request, *args, **kwargs)

class EditorHome(EditorRoleRequiredMixin, TemplateView):
    template_name = "editor/home.html"

class ListManuscripts(EditorRoleRequiredMixin, TemplateView):
    template_name = "editor/list_manuscripts.html"

    def get_context_data(self, **kwargs):
        c = super().get_context_data(**kwargs)
        qs = Manuscript.objects
        if 'q' in self.request.GET and self.request.GET['q']:
            qs = qs.filter(authors__username=self.request.GET['q'])
        qs = qs.count_reviews('num_reviews')
        qs = qs.count_reviews('num_complete_reviews', status=Review.StatusChoices.COMPLETE)
        for col, manuscripts in Manuscript.in_kanban_columns(qs.all()).items():
            c[col.name] = manuscripts
        return c
        
class ShowManuscript(EditorRoleRequiredMixin, DetailView):
    model = Manuscript

    def get(self, request, *args, **kwargs):
        m = self.get_object()
        return redirect('editor:show_revision', m.id, m.revisions.last().revision_number)

class ShowManuscriptReviews(EditorRoleRequiredMixin, DetailView):
    model = Manuscript

    def get(self, request, *args, **kwargs):
        m = self.get_object()
        return redirect('editor:show_revision_reviews', m.id, m.revisions.last().revision_number)

class ShowRevision(EditorRoleRequiredMixin, ManuscriptRevisionMixin, DetailView):
    model = Revision
    template_name = 'editor/manuscript_revision_detail.html'
    http_method_names = ['get', 'post']

    def __init__(self, *args, **kwargs):
        super(*args, **kwargs)
        self.object = None

    def get_context_data(self, **kwargs):
        c = super().get_context_data(**kwargs)
        revision = self.get_object()
        m = revision.manuscript
        missing_authorships = m.authorships.filter(acknowledged=False).all()
        missing_authors = [authorship.author for authorship in missing_authorships]
        c['is_waiting_for_authors'] = (len(missing_authors) > 0)
        if len(missing_authors) > 0:
            msg = "Waiting on authorship acknowledgement: {}"
            c['missing_authors_message'] = msg.format(m.format_names(missing_authors))

        # TODO this crashes
        #c['assign_reviewer_form'] = AssignReviewerForm(self.get_object())
        return c

    # TODO This belongs somewhere else...
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
                    review = Review.objects.create(
                        reviewer=user,
                        revision=manuscript.revisions.last(),
                        status=Review.StatusChoices.ASSIGNED,
                        date_due=datetime.now() + timedelta(days=settings.DAYS_TO_REVIEW)
                    )
                    notify_user_when_review_created(review)
                return redirect('editor:show_manuscript', manuscript.id)
            else:
                context['assign_reviewer_form'] = form
                return render(request, self.template_name, context)
        elif action.upper() == 'REMOVE_REVIEWER':
            user = manuscript.reviewers.get(username=request.POST['username'])
            Review.objects.filter(revision__manuscript=manuscript, reviewer=user).delete()
            manuscript.reviewers.remove(user)
            return redirect('editor:show_manuscript', manuscript.id)

class ShowRevisionReviews(EditorRoleRequiredMixin, ManuscriptRevisionMixin, DetailView):
    model = Revision
    template_name = 'editor/revision_reviews_detail.html'

class ListReviews(EditorRoleRequiredMixin, TemplateView):
    template_name = "editor/list_reviews.html"

    def get_context_data(self, **kwargs):
        c = super().get_context_data(**kwargs)
        qs = Review.objects
        if 'q' in self.request.GET and self.request.GET['q']:
            qs = qs.filter(reviewer__username=self.request.GET['q'])
        for col, reviews in Review.in_kanban_columns(qs.all()).items():
            c[col.name] = reviews
        return c
       
class ListIssues(EditorRoleRequiredMixin, ListView):
    model = JournalIssue
    template_name = "editor/list_issues.html"
    context_object_name = "issues"

class ShowIssue(EditorRoleRequiredMixin, DetailView):
    model = JournalIssue
    template_name = "editor/issue_detail.html"
    context_object_name = "issue"

class NewIssue(EditorRoleRequiredMixin, CreateView):
    model = JournalIssue
    form_class = NewJournalIssueForm
    template_name = "editor/new_issue.html"

    def get_success_url(self):
        return reverse('editor:show_issue', args=(self.object.id,))

class EditIssue(EditorRoleRequiredMixin, UpdateView):
    model = JournalIssue
    form_class = EditJournalIssueForm
    template_name = "editor/edit_issue.html"
    context_object_name = "issue"
    




