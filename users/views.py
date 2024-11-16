from django.shortcuts import render, redirect

# Create your views here.
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from users.forms import ProjectForm, JoinProjectForm
from django.http import HttpResponseRedirect, JsonResponse
from .models import Project
from django.urls import reverse
from .models import ProjectFiles, Comment 
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, get_object_or_404
from mysite.forms import UploadFileForm
import json


def index(request):
    return HttpResponse("Welcome to the homepage!")

@login_required
def create_project(request):
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
def join_private_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    
    # Redirect if project is not private or user is already a member
    if not project.is_private:
        return redirect('join_project')
    if request.user in project.collaborators.all() or project.user == request.user:
        return redirect('join_project')
    
    if request.method == "POST":
        password = request.POST.get('password')
        if project.password == password:
            project.collaborators.add(request.user)
            project.save()
            return redirect('common_default')
        else:
            return render(request, 'join_private_project.html', {
                'project': project,
                'error': 'Incorrect password'
            })
    
    return render(request, 'join_private_project.html', {'project': project})

@login_required
def join_project(request):
    if request.method == "POST":
        project_id = request.POST.get('project_id')
        try:
            project = Project.objects.get(id=project_id)
            
            if request.user in project.collaborators.all() or project.user == request.user:
                return render(request, 'joinproject.html', {
                    'projects': Project.objects.all().order_by('name'),
                    'error': 'You are already part of this project.'
                })
            elif project.is_private:
                return redirect('join_private_project', project_id=project.id)
            else:
                project.collaborators.add(request.user)
                project.save()
                return redirect('common_default')
                
        except Project.DoesNotExist:
            return render(request, 'joinproject.html', {
                'projects': Project.objects.all().order_by('name'),
                'error': 'Project not found.'
            })
    
    projects = Project.objects.all().order_by('name')
    return render(request, 'joinproject.html', {'projects': projects})
    
    # GET request - show all projects
    projects = Project.objects.all().order_by('name')
    return render(request, 'joinproject.html', {'projects': projects})

def audio_playback(request, file_id):
    audio_file = get_object_or_404(ProjectFiles, id=file_id)
    audio_url = audio_file.file.url
    
    # Get all comments for this audio file, ordered by timestamp
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
            return redirect('project_info', project_id=file_instance.project.id)
    else:
        form = UploadFileForm(instance=file_instance)
    return render(request, 'edit_metadata.html', {'form': form, 'file_instance': file_instance})