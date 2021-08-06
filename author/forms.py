from django import forms
from django.contrib.auth.models import User
from tinymce.widgets import TinyMCE
from .models import Revision

class NewManuscriptForm(forms.Form):
    title = forms.CharField(max_length=200)
    text = forms.CharField(widget=TinyMCE())
    additional_authors = forms.ModelMultipleChoiceField(queryset=None, required=False)

    def __init__(self, *args, **kwargs):
        try:
            current_user = kwargs.pop('current_user')
        except KeyError:
            raise ValueError("NewManuscriptForm must be passed current_user")
        super().__init__(*args, **kwargs)
        qs = User.objects.filter(profile__is_author=True).exclude(id=current_user.id).all()
        self.fields['additional_authors'].queryset=qs

    class Meta:
        model = Revision
        fields = ['title', 'text']
