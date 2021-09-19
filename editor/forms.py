from django import forms
from django.contrib.auth.models import User
from author.models import Manuscript, Revision
from reviewer.models import Review
from tinymce.widgets import TinyMCE
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

    introduction = forms.CharField(widget=TinyMCE()) 
    
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

class EditorialReviewForm(forms.ModelForm):
    editorial_review = forms.CharField(widget=TinyMCE())

    class Meta:
        model = Revision
        fields = ['editorial_review']

class EditorialDecisionForm(forms.ModelForm):
    """Allows the editor to issue a decision. 
    Uses Review.recommendation for convenience.
    """
    class Meta:
        model = Review
        fields = ['recommendation']
