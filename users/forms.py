from django import forms
from .models import Project, User

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'description', 'is_private']
        labels = {
            'is_private': 'Private',
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

class JoinProjectForm(forms.Form):
    project_name = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        help_text='Enter the name of the project you want to join'
    )
