from django import forms
from .models import Project

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'collaborators']  
        widgets = {
            'collaborators': forms.CheckboxSelectMultiple()  
        }

class JoinProjectForm(forms.Form):
    project_name = forms.CharField(max_length=255, label='Project Name')
