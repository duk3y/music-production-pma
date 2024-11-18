from django import forms
from users.models import ProjectFiles, Task, User

class UploadFileForm(forms.ModelForm):
    class Meta:
        model = ProjectFiles
        fields = ['file', 'title', 'description', 'keywords']
        widgets = {
            'keywords': forms.TextInput(attrs={'placeholder': 'Enter keywords separated by commas'}),
        }
        
class DateInput(forms.DateInput):
    input_type = 'date'

class CreateTaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['name','description','deadline', 'assignees']
        widgets = {
            'name': forms.TextInput(attrs={'size':'30'}),
            'deadline': forms.DateInput(attrs={'type': 'datetime-local'}),
            'assignees': forms.CheckboxSelectMultiple,
        }
    def __init__(self, *args, project_id = None, **kwargs):
        super(CreateTaskForm, self).__init__(*args,**kwargs)
        
        if project_id:
            self.fields['assignees'].queryset = User.objects.filter(collaborating_projects__id=project_id, )

