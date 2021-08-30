from django import forms
from tinymce.widgets import TinyMCE
from .models import Review

class EditReviewForm(forms.ModelForm):
    text = forms.CharField(widget=TinyMCE())

    class Meta:
        model = Review
        fields = ['text', 'recommendation']
