from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse
from django.views import View
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, HttpResponseForbidden
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from users.models import DiscussionComment, Profile, Project, ProjectFiles, Task
from users.forms import ProjectForm 
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import UploadFileForm, CreateTaskForm
from django.utils.timezone import now

import json

@login_required
def CalendarView(request):
    user = request.user
    
    return render(request, 'calendar.html')


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

@login_required
def create_task(request, project_id):
    project = Project.objects.get(id=project_id)

    if request.method == "POST":
        form = CreateTaskForm(request.POST, project_id=project_id)
        if form.is_valid():
            task = form.save(commit=False)
            task.project = project
            task.save()
            form.save_m2m()
            return HttpResponseRedirect(reverse('project_task_view', args=[project_id]))
    else:
        form = CreateTaskForm()
    return render(request, 'create_task.html', {'form': form})

def delete_file(request, file_id):
    file = get_object_or_404(ProjectFiles, id=file_id)
    file.delete()
    
    # Redirect to the project information page after deletion
    return redirect('project_info', project_id=file.project.id)

def manage_files(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    context = {'project': project}
    return render(request, 'manage_files.html', context)


def home(request):
    return render(request, 'home.html')

def public_projects(request):
    public_projects = Project.objects.filter(is_private=False)  # Filter to only get public projects
    return render(request, 'public_projects.html', {'public_projects': public_projects})

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
def project_files_view(request, project_id):
    project = Project.objects.get(id=project_id)
    files = ProjectFiles.objects.filter(project=project)

    # video_files = files.filter(file__iendswith=('.mp4', '.mov', '.avi'))
    video_files = (files.filter(file__icontains='.mp4') | files.filter(file__icontains='.mov') | files.filter(file__icontains='.avi')).distinct()
    image_files = (files.filter(file__icontains='.jpg') | files.filter(file__icontains='.jpeg') | files.filter(file__icontains='.png') | files.filter(file__icontains='.gif')).distinct()
    text_files = (files.filter(file__icontains='.txt') | files.filter(file__icontains='.pdf') | files.filter(file__icontains='.docx')).distinct()
    audio_files = (files.filter(file__icontains='.mp3') | files.filter(file__icontains='.wav') | files.filter(file__icontains='.aac')).distinct()

    return render(request, 'project_files.html', {
        'project': project,
        'video_files': video_files,
        'image_files': image_files,
        'text_files': text_files,
        'audio_files' : audio_files,
    })

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

@login_required()
def ProjectTaskView(request, project_id):
    project = Project.objects.get(id=project_id)
    tasks = Task.objects.filter(project=project)

    to_do_tasks = tasks.filter(status = "to do")
    in_progress_tasks = tasks.filter(status = 'in progress')
    waiting_approval_tasks = tasks.filter(status = 'waiting approval')
    completed_tasks = tasks.filter(status = "done")

    return render(request, 'project_tasks.html',{
        'project': project,
        'to_do_tasks': to_do_tasks,
        'in_progress_tasks': in_progress_tasks,
        'waiting_approval_tasks': waiting_approval_tasks,
        'completed_tasks': completed_tasks
    })

@login_required()
def TaskInfoView(request, task_id, project_id):
    project = Project.objects.get(id=project_id)
    task = Task.objects.get(id=task_id)
    task = get_object_or_404(Task, id=task_id)
    return render(request, 'task_info.html', {'task': task, 'project': project})

def login_redirect(request):
    user = request.user
    profile = Profile.objects.get(user=user)

    if profile.pmaStatus:
        return redirect('pma_admin_default')
    else:
        return redirect('common_default')
    
@login_required
def edit_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if request.method == 'POST':
        # Update the project details
        project.name = request.POST.get('name')
        project.description = request.POST.get('description')
        project.save()
        return redirect('project_info', project_id=project.id)
    
    # Render the edit form
    return render(request, 'edit_project.html', {'project': project})

def user_tasks(request):
    user = request.user
    tasks = Task.objects.filter(assignees=user)
    
    events = [
        {
            'title': task.name,
            'start': task.deadline.isoformat(),
            'description': task.description,
            'id': task.id

        }
        for task in tasks
    ]

    return JsonResponse(events, safe=False)

@login_required
def delete_task(request, project_id, task_id):
    task = Task.objects.get(id=task_id)
    task.delete()

    return redirect(reverse('project_task_view', args=[project_id]))

@login_required
def updateTaskStatus(request):
    data = json.loads(request.body)

    task_id = data.get('task_id')
    new_status = data.get('new_status')

    task = Task.objects.get(id=task_id)
    task.status = new_status
    task.save()

    return JsonResponse({'success': True})

@login_required
def add_project_comment(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    if request.method == 'POST':
        comment_text = request.POST.get('comment')
        if comment_text:
            DiscussionComment.objects.create(
                project=project,
                user=request.user,
                text=comment_text
            )
            return redirect('project_info', project_id=project.id)
    else:
        return HttpResponse("Invalid request method", status=405)

@login_required
def resolve_discussion_comment(request, comment_id):
    comment = get_object_or_404(DiscussionComment, id=comment_id)
    # Optional: Only allow the comment creator or project owner to delete
    if comment.user != request.user and comment.project.user != request.user:
        return HttpResponseForbidden("You are not allowed to resolve this comment.")
    
    project_id = comment.project.id
    comment.delete()
    return redirect('project_info', project_id=project_id)
