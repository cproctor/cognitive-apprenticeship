from datetime import datetime
from django.db import transaction, DatabaseError
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, FormView
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from .models import Manuscript, ManuscriptAuthorship, Revision
from .forms import NewManuscriptForm

class AuthorRoleRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            msg = "You must be logged in to view authors pages."
            messages.add_message(request, messages.WARNING, msg)
            return redirect('home_page')
        if not request.user.profile.is_author:
            msg = "You are not registered as an author."
            messages.add_message(request, messages.WARNING, msg)
            return redirect('home_page')
        return super().dispatch(request, *args, **kwargs)

class AuthorHome(AuthorRoleRequiredMixin, TemplateView):
    template_name = "author/home.html"
    
    def get_context_data(self):
        return {
            'manuscripts': Manuscript.objects.filter(authors=self.request.user),
        }

class NewManuscript(AuthorRoleRequiredMixin, FormView):
    form_class = NewManuscriptForm
    template_name = "author/new_manuscript.html"

    def get_form(self):
        return NewManuscriptForm(current_user=self.request.user)

    def post(self, request, *args, **kwargs):
        form = NewManuscriptForm(request.POST, current_user=request.user)
        if form.is_valid():
            try:
                with transaction.atomic():
                    manuscript = Manuscript.objects.create()
                    ManuscriptAuthorship.objects.create(
                        manuscript=manuscript, 
                        author=request.user,
                        acknowledged=True
                    )
                    for author in form.cleaned_data['additional_authors']:
                        manuscript.authors.add(author)
                    if manuscript.has_unacknowledged_authors():
                        status = Revision.StatusChoices.WAITING_FOR_AUTHORS
                    else:
                        status = Revision.StatusChoices.UNSUBMITTED
                    revision = manuscript.revisions.create(
                        revision_number=0,
                        title=form.cleaned_data['title'],
                        text=form.cleaned_data['text'],
                        date_created=datetime.now(),
                        status=status,
                    )
                return redirect('show_revision', manuscript_pk=manuscript.id,
                        revision_number=revision.revision_number)
            except DatabaseError:
                return render(request, self.template_name, {'form': form})
        else:
            return render(request, self.template_name, {'form': form})

class ShowManuscript(AuthorRoleRequiredMixin, DetailView):
    model = Manuscript

    def get(self, request, *args, **kwargs):
        m = self.get_object()
        if m.revisions.count() == 1:
            return redirect('show_revision', m.id, m.revisions.last().revision_number)
        return super().get(request, *args, **kwargs)

class ShowRevision(AuthorRoleRequiredMixin, DetailView):
    model = Revision
    context_object_name = "revision"

    def get_object(self, queryset=None):
        qs = queryset or self.get_queryset()
        try:
            qs = Revision.objects.filter(
                manuscript__id=self.kwargs['manuscript_pk'],
                revision_number=self.kwargs['revision_number']
            )
            return qs.get()
        except Revision.DoesNotExist:
            raise Http404("No such revision")


