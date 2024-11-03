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
    audio_file = get_object_or_404(ProjectFiles, id=file_id)
    audio_url = audio_file.file.url  # Assuming `file` is the field with the audio file

    # If `comments` is a related field to `ProjectFiles` model
    comments = audio_file.comments.all() if hasattr(audio_file, 'comments') else []

    return render(request, 'audio_playback.html', {
        'audio': audio_file,
        'audio_url': audio_url,
        'comments': comments,
    })


def add_comment(request, project_file_id):
    if request.method == 'POST':
        project_file = get_object_or_404(ProjectFiles, id=project_file_id)
        timestamp = float(request.POST.get('timestamp'))
        text = request.POST.get('text')
        user = request.user if request.user.is_authenticated else None

        # Save the comment
        Comment.objects.create(
            project=project_file.project,
            timestamp=timestamp,
            text=text,
            user=user
        )
        return redirect('audio_playback', project_file_id=project_file_id)

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