from django import forms
from users.models import ProjectFiles

class UploadFileForm(forms.ModelForm):
    class Meta:
        model = ProjectFiles
        fields = ['file']