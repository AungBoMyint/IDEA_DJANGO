from ckeditor.widgets import CKEditorWidget
from django import forms

class BlogLinkForm(forms.ModelForm):
    body = forms.CharField(widget=CKEditorWidget)