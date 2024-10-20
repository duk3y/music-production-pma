from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import View
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from users.models import Profile, Project, ProjectFiles
from .forms import UploadFileForm

@login_required()
def upload_file(request, project_id):
    project = Project.objects.get(id=project_id)

    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            projectfile = form.save(commit=False)
            projectfile.project = project
            projectfile.uploaded_by = request.user
            projectfile.save()
    else:
        form = UploadFileForm()
    return render(request, "upload.html", {"form":form})

@login_required()
def view_files(request, project_id):
    project = Project.objects.get(id=project_id)
    files = ProjectFiles.objects.filter(project=project)

    return render(request, 'showprojectfiles.html',{"files": files})

def home(request):
    return render(request, 'home.html')

class CustomLoginView(LoginView):
    template_name = 'login.html'

class CommonDefaultView(View):
    template_name = 'commondefault.html'

    def get(self, request):
        user = request.user
        owned_projects = Project.objects.filter(user=user)
        collaborating_projects = Project.objects.filter(collaborators=user)

        # combine owned and collaborating projects
        projects = owned_projects | collaborating_projects

        context = {
            'projects': projects.distinct(),
            'username': user.username
        }
        print("Rendering commondefault.html with", len(projects), "projects")
        return render(request, self.template_name, context)

class PMAAdminDefaultView(View):
    template_name = 'pmaadmindefault.html'

    def get(self, request):
        return render(request, self.template_name)


@login_required()
def AuthenticationView(request):
    user = request.user
    profile = Profile.objects.get(user=user)

    # print(Profile.pmaStatus)
    if profile.pmaStatus:
        print("yes")
        return redirect(reverse("pma_admin_default"))
    else:
        print("no")
        return redirect(reverse("common_default"))

@login_required()
def ProjectDetailView(request, project_id):
    project = Project.objects.get(id=project_id)
    return render(request, 'project_info.html', {'project':project})

