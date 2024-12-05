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
from django.db.models import Q
from django.contrib import messages

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

class ManageFilesAdminView(View):
    template_name = 'manage_files_admin.html'

    def dispatch(self, request, *args, **kwargs):
        # Check if the user is logged in and has pmaStatus
        if not request.user.is_authenticated:
            return redirect('login')  # Redirect to login if not authenticated

        try:
            profile = Profile.objects.get(user=request.user)
            if not profile.pmaStatus:
                return HttpResponseForbidden("You do not have permission to access this page.")
        except Profile.DoesNotExist:
            return HttpResponseForbidden("You do not have permission to access this page.")

        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        files = ProjectFiles.objects.select_related('project', 'uploaded_by')
        context = {
            'files': files,
            'username': request.user.username,
        }
        return render(request, self.template_name, context)

@login_required()
def AuthenticationView(request):
    user = request.user
    profile = Profile.objects.get(user=user)

    # print(Profile.pmaStatus)
    if profile.pmaStatus:
        print("yes")
        return redirect(reverse("manage_files_admin"))
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
        return redirect('manage_files_admin')
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

from django.http import HttpResponseForbidden

@login_required
def resolve_discussion_comment(request, comment_id):
    comment = get_object_or_404(DiscussionComment, id=comment_id)
    project = comment.project
    
    if request.user != comment.user and request.user != project.user:
        return HttpResponseForbidden("You are not allowed to resolve this comment.")

    comment.delete()
    return redirect('project_info', project_id=project.id)

@login_required
def search_files(request, project_id):
    project = Project.objects.get(id=project_id)
    query = request.GET.get("query", "").strip()
    if query:
        files = ProjectFiles.objects.filter(
            project=project
        ).filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(keywords__icontains=query)
        )
    else:
        return redirect('manage_project_files', project_id=project_id)

    return render(request, 'project_files.html', {
        'project': project,
        'files': files,
        'query': query,
    })

@login_required
def confirm_delete_project(request, project_id):
    project = get_object_or_404(Project, id=project_id, user=request.user)

    return render(request, 'confirm_delete_project.html', {
        'project': project
    })

@login_required
def delete_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    # Ensure only PMA admins or project owners can delete
    if not (request.user.profile.pmaStatus or project.user == request.user):
        return HttpResponseForbidden("You do not have permission to delete this project.")

    if request.method == 'POST':
        project.delete()
        messages.success(request, f'Project "{project.name}" was deleted successfully.')
        return redirect('manage_projects_admin')  # Redirect to manage projects for admins

    return redirect('manage_projects_admin')  # Fallback redirect


@login_required
def delete_file_from_manage(request, file_id):
    file = get_object_or_404(ProjectFiles, id=file_id)
    project = file.project

    if request.user == file.uploaded_by or request.user.profile.pmaStatus:
        file.delete()
        messages.success(request, "File deleted successfully.")
    else:
        messages.error(request, "You do not have permission to delete this file.")

    return redirect('manage_project_files', project_id=project.id)

@login_required
def delete_file_from_admin(request, file_id):
    file = get_object_or_404(ProjectFiles, id=file_id)

    if request.user == file.uploaded_by or request.user.profile.pmaStatus:
        file.delete()
        messages.success(request, "File deleted successfully.")
    else:
        messages.error(request, "You do not have permission to delete this file.")

    return redirect('manage_files_admin')


class ManageProjectsAdminView(LoginRequiredMixin, View):
    template_name = 'manage_projects_admin.html'
    login_url = '/login/'  # Redirect to login if unauthenticated

    def dispatch(self, request, *args, **kwargs):
        # Ensure the user is a PMA admin
        try:
            profile = request.user.profile
            if not profile.pmaStatus:
                return HttpResponseForbidden("You do not have permission to access this page.")
        except AttributeError:
            return HttpResponseForbidden("You do not have permission to access this page.")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        projects = Project.objects.all()  # Fetch all projects
        context = {
            'projects': projects,
        }
        return render(request, self.template_name, context)
