from django import forms
from django.contrib.auth.models import User
from author.models import Manuscript, Revision
from .models import JournalIssue

class AssignReviewerForm(forms.Form):
    """A form for adding a User as a reviewer.
    """
    reviewer = forms.ModelChoiceField(queryset=None, required=True)

    def __init__(self, manuscript, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.possible_reviewers = (
            User.objects
            .filter(profile__is_reviewer=True)
            .exclude(manuscripts=manuscript)
            .exclude(reviewed_manuscripts=manuscript)
        )
        self.fields['reviewer'].queryset = self.possible_reviewers

    def num_possible_reviewers(self):
        return bool(len(self.possible_reviewers))

class NewJournalIssueForm(forms.ModelForm):
    
    class Meta:
        model = JournalIssue
        fields = ['title', 'introduction', 'volume', 'number']

class EditJournalIssueForm(forms.ModelForm):
    
    manuscripts = forms.ModelMultipleChoiceField(
        queryset=Manuscript.objects.filter(revisions__status__in=[
            Revision.StatusChoices.ACCEPT, 
            Revision.StatusChoices.PUBLISHED,
        ]),
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = JournalIssue
        fields = ['title', 'introduction', 'volume', 'number', 'published', 'manuscripts']
