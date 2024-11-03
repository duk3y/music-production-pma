from django import forms
from users.models import ProjectFiles

class UploadFileForm(forms.ModelForm):
    class Meta:
        model = ProjectFiles
        fields = ['file', 'title', 'description', 'keywords']
        widgets = {
            'keywords': forms.TextInput(attrs={'placeholder': 'Enter keywords separated by commas'}),
        }