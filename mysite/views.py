from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse
from django.views import View
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from users.models import Profile, Project, ProjectFiles
from users.forms import ProjectForm 
from .forms import UploadFileForm
from django.contrib.auth.mixins import LoginRequiredMixin


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
            return redirect('project_info', project_id=project.id) 
    else:
        form = UploadFileForm()
    return render(request, "upload.html", {"form": form, "project": project})


def home(request):
    return render(request, 'home.html')

class CustomLoginView(LoginView):
    template_name = 'login.html'

class CommonDefaultView(LoginRequiredMixin, View):
    template_name = 'commondefault.html'
    login_url = '/login/'  # Specify the login URL
    redirect_field_name = 'next'

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
    files = ProjectFiles.objects.filter(project=project)

    # video_files = files.filter(file__iendswith=('.mp4', '.mov', '.avi'))
    video_files = (files.filter(file__icontains='.mp4') | files.filter(file__icontains='.mov') | files.filter(file__icontains='.avi')).distinct()
    image_files = (files.filter(file__icontains='.jpg') | files.filter(file__icontains='.jpeg') | files.filter(file__icontains='.png') | files.filter(file__icontains='.gif')).distinct()
    text_files = (files.filter(file__icontains='.txt') | files.filter(file__icontains='.pdf') | files.filter(file__icontains='.docx')).distinct()
    audio_files = (files.filter(file__icontains='.mp3') | files.filter(file__icontains='.wav') | files.filter(file__icontains='.aac')).distinct()

    return render(request, 'project_info.html', {
        'project': project,
        'video_files': video_files,
        'image_files': image_files,
        'text_files': text_files,
        'audio_files' : audio_files,
    })

def login_redirect(request):
    user = request.user
    profile = Profile.objects.get(user=user)

    if profile.pmaStatus:
        return redirect('pma_admin_default')
    else:
        return redirect('common_default')

