from datetime import datetime
from django.db import transaction, DatabaseError
from django.http import HttpResponseForbidden
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, FormView
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from .models import Manuscript, ManuscriptAuthorship, Revision
from .forms import NewManuscriptForm, EditRevisionForm
from .mixins import (
    AuthorMixin,
    ManuscriptRevisionMixin,
)

class AuthorHome(AuthorMixin, TemplateView):
    template_name = "author/home.html"
    
    def get_context_data(self):
        my_manuscripts = Manuscript.objects.filter(authors=self.request.user).all()
        return {
            'manuscripts_in_preparation': [m for m in my_manuscripts if m.process_stage() == "in preparation"],
            'manuscripts_in_submission': [m for m in my_manuscripts if m.process_stage() == "in submission"],
            'manuscripts_decided': [m for m in my_manuscripts if m.process_stage() == "decided"],
            'manuscripts_published': [m for m in my_manuscripts if m.process_stage() == "published"],
        }

class NewManuscript(AuthorMixin, FormView):
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
                return redirect('author:show_revision', manuscript_pk=manuscript.id,
                        revision_number=revision.revision_number)
            except DatabaseError:
                return render(request, self.template_name, {'form': form})
        else:
            return render(request, self.template_name, {'form': form})

class ShowManuscript(AuthorMixin, DetailView):
    """Redirects to show the manuscript's last revision.
    """
    model = Manuscript

    def get_queryset(self):
        return Manuscript.objects.filter(authors=self.request.user)

    def get(self, request, *args, **kwargs):
        m = self.get_object()
        return redirect('author:show_revision', m.id, m.revisions.last().revision_number)

class ShowRevision(AuthorMixin, ManuscriptRevisionMixin, DetailView):
    http_method_names = ['get', 'post']
    model = Revision

    def post(self, request, *args, **kwargs):
        revision = self.get_object()
        action = request.POST['action'].upper()
        try:
            if action == "SUBMIT":
                if revision.can_submit():
                    return self.submit_revision()
                else:
                    raise ActionNotAllowed("submit")
            elif action == "WITHDRAW":
                if revision.can_withdraw():
                    return self.withdraw_revision()
                else:
                    raise ActionNotAllowed("withdraw")
            elif action == "CREATE A NEW REVISION":
                if revision.can_create_new_revision():
                    return self.create_new_revision()
                else:
                    raise ActionNotAllowed("new revision")
            else:
                return HttpResponseForbidden("Unrecognized action")
        except ActionNotAllowed as e:
            messages.add_message(request, messages.WARNING, str(e))
            return HttpResponseForbidden(str(e))

    def submit_revision(self):
        revision = self.get_object()
        revision.status = revision.StatusChoices.PENDING
        revision.date_submitted = datetime.now()
        revision.save()
        message = "Your manuscript has been submitted. You will be notified once reviewers provide feedback."
        messages.add_message(self.request, messages.INFO, message)
        return redirect(
            'author:show_revision', 
            manuscript_pk=revision.manuscript_id,
            revision_number=revision.revision_number
        )

    def withdraw_revision(self):
        revision = self.get_object()
        revision.status = revision.StatusChoices.WITHDRAWN
        revision.date_decided = datetime.now()
        revision.save()
        message = "Your manuscript has been withdrawn and will not be reviewed."
        messages.add_message(self.request, messages.INFO, message)
        return redirect(
            'author:show_revision', 
            manuscript_pk=revision.manuscript_id,
            revision_number=revision.revision_number
        )

    def create_new_revision(self):
        revision = self.get_object()
        new_revision = revision.create_new_revision()
        message = "You have created a new revision."
        messages.add_message(self.request, messages.INFO, message)
        return redirect(
            'author:show_revision', 
            manuscript_pk=revision.manuscript_id,
            revision_number=new_revision.revision_number
        )

class EditRevision(AuthorMixin, ManuscriptRevisionMixin, UpdateView):
    model = Revision
    form_class = EditRevisionForm
    template_name = "author/edit_revision.html"

    def get_success_url(self):
        revision = self.get_object()
        return reverse('author:show_revision', args=(revision.manuscript_id, 
                revision.revision_number))

class ActionNotAllowed(Exception):
    def __init__(self, action):
        super().__init__("Action {} not allowed")
