from django.core.exceptions import ValidationError
from django import forms
from django.contrib.auth.models import User
from roles.models import Profile

class ProfileForm(forms.Form):
    first_name = forms.CharField(min_length=1)
    last_name = forms.CharField(min_length=1)

    def __init__(self, data, user):
        super().__init__(data)
        self.user = user
