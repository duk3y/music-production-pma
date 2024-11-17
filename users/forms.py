from django import forms
from .models import Project

class ProjectForm(forms.ModelForm):
    is_private = forms.BooleanField(required=False, label='Make this project private')
    password = forms.CharField(
        widget=forms.PasswordInput(),
        required=False,
        label='Project Password'
    )

    class Meta:
        model = Project
        fields = ['name', 'is_private', 'password']

    def clean(self):
        cleaned_data = super().clean()
        is_private = cleaned_data.get('is_private')
        password = cleaned_data.get('password')

        if is_private and not password:
            raise forms.ValidationError("Private projects require a password")
        return cleaned_data


class JoinProjectForm(forms.Form):
    project_name = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'id': 'id_project_name',
            'placeholder': 'Enter project name'
        })
    )
    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'id': 'id_password',
            'placeholder': 'Enter project password (if required)'
        })
    )
