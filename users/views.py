from django.shortcuts import render, redirect, get_object_or_404

# Create your views here.
from django.http import HttpResponse, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from users.forms import ProjectForm, JoinProjectForm
from django.http import HttpResponseRedirect, JsonResponse
from .models import Project, Profile, ProjectFiles, Comment 
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, get_object_or_404
from mysite.forms import UploadFileForm, CreateTaskForm
import json
from django.template.defaultfilters import register
from django.contrib import messages
from django.db.models import Q


def index(request):
    return HttpResponse("Welcome to the homepage!")

def public_projects(request):
    # View for listing public projects
    public_projects = Project.objects.filter(is_private=False)
    return render(request, 'public_projects.html', {'public_projects': public_projects})

@login_required
def create_project(request):
    # Check if the user is a PMA admin
    try:
        profile = Profile.objects.get(user=request.user)
        if profile.pmaStatus:
            return HttpResponseForbidden("PMA admins are not allowed to create projects.")
    except Profile.DoesNotExist:
        return HttpResponseForbidden("You do not have permission to perform this action.")

    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.user = request.user
            project.save()
            form.save_m2m()
            return HttpResponseRedirect(reverse('common_default'))
    else:
        form = ProjectForm()
    return render(request, 'createproject.html', {'form': form})

@login_required
def join_project_list(request):
    try:
        profile = Profile.objects.get(user=request.user)
        if profile.pmaStatus:
            return HttpResponseForbidden("PMA admins are not allowed to join projects.")
    except Profile.DoesNotExist:
        return HttpResponseForbidden("You do not have permission to perform this action.")

    projects = Project.objects.exclude(
        Q(user=request.user) | Q(collaborators=request.user)
    ).distinct()
    return render(request, 'join_project_list.html', {'projects': projects})


@login_required
def join_project(request, project_id=None):
    try:
        profile = Profile.objects.get(user=request.user)
        if profile.pmaStatus:
            return HttpResponseForbidden("PMA admins are not allowed to join projects.")
    except Profile.DoesNotExist:
        return HttpResponseForbidden("You do not have permission to perform this action.")

    if project_id:
        project = get_object_or_404(Project, id=project_id)

        if request.user in project.collaborators.all() or project.user == request.user:
            messages.warning(request, 'You are already part of this project.')
            return redirect('common_default')

        if project.is_private:
            return redirect('join_private_project', project_id=project_id)

        project.collaborators.add(request.user)
        project.save()
        messages.success(request, f'Successfully joined {project.name}!')
        return redirect('common_default')

    projects = Project.objects.exclude(
        Q(user=request.user) | Q(collaborators=request.user)
    ).distinct()

    return render(request, 'joinproject.html', {'projects': projects})


@login_required
def join_private_project(request, project_id):
    try:
        profile = Profile.objects.get(user=request.user)
        if profile.pmaStatus:
            return HttpResponseForbidden("PMA admins are not allowed to join private projects.")
    except Profile.DoesNotExist:
        return HttpResponseForbidden("You do not have permission to perform this action.")

    project = get_object_or_404(Project, id=project_id)
    error = None

    if request.method == "POST":
        password = request.POST.get('password')
        if password == project.password:
            project.collaborators.add(request.user)
            project.save()
            messages.success(request, f'Successfully joined {project.name}!')
            return redirect('common_default')
        else:
            error = "Incorrect password"

    return render(request, 'join_private_project.html', {
        'project': project,
        'error': error
    })


def audio_playback(request, file_id):
    print(f"Accessing audio_playback with file_id: {file_id}")  
    audio_file = get_object_or_404(ProjectFiles, id=file_id)
    audio_url = audio_file.file.url
    
    comments = Comment.objects.filter(file=audio_file).order_by('timestamp')
    
    context = {
        'audio': audio_file,
        'audio_url': audio_url,
        'comments': comments,
    }
    return render(request, 'audio_playback.html', context)

@login_required
def add_comment(request, file_id):
    if request.method == 'POST':
        audio_file = get_object_or_404(ProjectFiles, id=file_id)
        
        # Get the form data
        timestamp = float(request.POST.get('timestamp', 0))
        text = request.POST.get('text', '').strip()
        
        if text:  # Only create comment if there's actual text
            Comment.objects.create(
                file=audio_file,
                timestamp=timestamp,
                text=text,
                user=request.user
            )
        
        return redirect('audio_playback', file_id=file_id)
    
    return redirect('audio_playback', file_id=file_id)

@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    file_id = comment.file.id  # Store the file_id before deleting the comment
    
    # Only allow the comment owner or project admin to delete
    if request.user == comment.user or request.user == comment.file.project.user:
        comment.delete()
    
    return redirect('audio_playback', file_id=file_id)

@login_required
def edit_metadata(request, file_id):
    file_instance = get_object_or_404(ProjectFiles, id=file_id)

    if request.method == 'POST':
        form = UploadFileForm(request.POST, instance=file_instance)
        if form.is_valid():
            form.save()
            return redirect('project_files', project_id=file_instance.project.id)
    else:
        form = UploadFileForm(instance=file_instance)
    return render(request, 'edit_metadata.html', {'form': form, 'file_instance': file_instance})

@login_required
def upload_file(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file_instance = form.save(commit=False)
            file_instance.project = project
            file_instance.uploaded_by = request.user
            file_instance.save()
            
            # Check if audio file and redirect
            file_ext = file_instance.file.name.split('.')[-1].lower()
            if file_ext in ['mp3', 'wav', 'ogg', 'm4a']:
                return redirect('audio_playback', file_id=file_instance.id)
            
            return redirect('project_files', project_id=project_id)
    else:
        form = UploadFileForm()
    return render(request, 'upload.html', {'form': form})

@login_required
def project_files(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    
    # Filter for audio files based on file extension
    audio_files = ProjectFiles.objects.filter(
        project=project,
        file__endswith=('.mp3', '.wav', '.ogg', '.m4a')
    )
    
    context = {
        'project': project,
        'audio_files': audio_files,
    }
    return render(request, 'project_files.html', context)

@register.filter
def endswith(value, arg):
    return value.endswith(arg)

