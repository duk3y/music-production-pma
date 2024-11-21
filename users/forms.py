from django import forms
from .models import Project, User

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'description', 'is_private', 'password']
        labels = {
            'is_private': 'Private',  # Changed from "Is private" to "Private"
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'password': forms.PasswordInput(),
        }

    def clean(self):
        cleaned_data = super().clean()
        is_private = cleaned_data.get('is_private')
        password = cleaned_data.get('password')

        if is_private and not password:
            raise forms.ValidationError("Private projects require a password")
        
        return cleaned_data

class JoinProjectForm(forms.Form):
    project_name = forms.CharField(max_length=255)
    password = forms.CharField(widget=forms.PasswordInput(), required=False)

    def clean(self):
        cleaned_data = super().clean()
        project_name = cleaned_data.get('project_name')
        password = cleaned_data.get('password')

        try:
            project = Project.objects.get(name=project_name)
            if project.is_private and not password:
                raise forms.ValidationError("This is a private project. Please enter the password.")
            if project.is_private and password != project.password:
                raise forms.ValidationError("Incorrect password")
        except Project.DoesNotExist:
            raise forms.ValidationError("No project found with that name")

        return cleaned_data
