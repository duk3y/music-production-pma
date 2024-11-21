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
from mysite.forms import UploadFileForm, CreateTaskForm
import json
from django.template.defaultfilters import register


def index(request):
    return HttpResponse("Welcome to the homepage!")

@login_required
def create_project(request):
    print(f'User in create_project outside post: {request.user}')
    if request.method == "POST":
        print(f'User in create_project: {request.user}')
        form = ProjectForm(request.POST, request_user=request.user)
        if form.is_valid():
            project = form.save(commit=False)
            project.user = request.user
            project.save()
            form.save_m2m()
            project.collaborators.add(request.user)
            return HttpResponseRedirect(reverse('common_default'))
    else:
        form = ProjectForm()
    return render(request, 'createproject.html', {'form': form})

@login_required
def join_project(request):
    if request.method == "POST":
        form = JoinProjectForm(request.POST)
        if form.is_valid():
            project_name = form.cleaned_data['project_name']
            try:
                project = Project.objects.get(name=project_name)
                
                if request.user in project.collaborators.all() or project.user == request.user:
                    form.add_error('project_name', 'You are already part of this project.')
                else:
                    project.collaborators.add(request.user)
                    project.save()
                    return redirect('common_default')
            except Project.DoesNotExist:
                form.add_error('project_name', 'No project found with that name.')
    else:
        form = JoinProjectForm()

    return render(request, 'joinproject.html', {'form': form})

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

