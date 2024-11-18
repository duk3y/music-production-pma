from django import forms
from .models import Project, User

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name','description','collaborators']  
        widgets = {
            'collaborators': forms.CheckboxSelectMultiple()  
        }
    def __init__(self, *args, request_user = None, **kwargs):
        super(ProjectForm, self).__init__(*args,**kwargs)
        print(f'request user: {request_user}')
        if request_user:
            self.fields['collaborators'].queryset = User.objects.exclude(id=request_user.id)
            print(f"exclusion: {request_user.id}")



class JoinProjectForm(forms.Form):
    project_name = forms.CharField(max_length=255, label='Project Name')
