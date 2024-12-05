from django.shortcuts import render, redirect, get_object_or_404

# Create your views here.
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from users.forms import ProjectForm, JoinProjectForm
from django.http import HttpResponseRedirect, HttpResponseForbidden, JsonResponse
from .models import Project
from django.urls import reverse
from .models import ProjectFiles, Comment, ProjectJoinRequest
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
    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.user = request.user
            project.save()
            return HttpResponseRedirect(reverse('common_default'))
    else:
        form = ProjectForm()
    return render(request, 'createproject.html', {'form': form})

@login_required
def join_project_list(request):
    # Show list of all projects available to join
    projects = Project.objects.exclude(
        Q(user=request.user) | Q(collaborators=request.user)
    ).distinct()
    return render(request, 'join_project_list.html', {'projects': projects})

@login_required
def join_project(request, project_id=None):
    if project_id:
        project = get_object_or_404(Project, id=project_id)
        
        # Check if user is already part of the project
        if request.user in project.collaborators.all() or project.user == request.user:
            messages.warning(request, 'You are already part of this project.')
            return redirect('common_default')
        
        # Only allow joining public projects through this view
        if project.is_private:
            return redirect('join_private_project', project_id=project_id)
        
        # Add user to public project
        project.collaborators.add(request.user)
        project.save()
        messages.success(request, f'Successfully joined {project.name}!')
        return redirect('common_default')
    
    # Display list of available projects
    projects = Project.objects.exclude(
        Q(user=request.user) | Q(collaborators=request.user)
    ).distinct()
    
    return render(request, 'joinproject.html', {'projects': projects})

@login_required
def join_private_project(request, project_id):
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

@login_required
def request_to_join(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    
    # Check if user is already a member
    if request.user in project.collaborators.all() or project.user == request.user:
        messages.error(request, 'You are already a member of this project.')
        return redirect('common_default')
        
    # Check if there's already a pending request
    existing_request = ProjectJoinRequest.objects.filter(
        project=project,
        user=request.user,
        status='pending'
    ).exists()
    
    if existing_request:
        messages.info(request, 'You already have a pending request for this project.')
        return redirect('common_default')
        
    # Create new request
    ProjectJoinRequest.objects.create(
        project=project,
        user=request.user
    )
    messages.success(request, 'Join request sent successfully.')
    return redirect('common_default')

@login_required
def manage_join_requests(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    
    # Ensure user is the project owner
    if request.user != project.user:
        return HttpResponseForbidden("You don't have permission to manage join requests.")
        
    pending_requests = ProjectJoinRequest.objects.filter(
        project=project,
        status='pending'
    )
    
    return render(request, 'manage_join_requests.html', {
        'project': project,
        'pending_requests': pending_requests
    })

@login_required
def handle_join_request(request, request_id, action):
    join_request = get_object_or_404(ProjectJoinRequest, id=request_id)
    project = join_request.project
    
    # Ensure user is the project owner
    if request.user != project.user:
        return HttpResponseForbidden("You don't have permission to handle join requests.")
        
    if action == 'approve':
        join_request.status = 'approved'
        project.collaborators.add(join_request.user)
        messages.success(request, f'Added {join_request.user.username} to the project.')
    elif action == 'reject':
        join_request.status = 'rejected'
        messages.info(request, f'Rejected {join_request.user.username}\'s request.')
        
    join_request.save()
    return redirect('manage_join_requests', project_id=project.id)

@login_required
def project_info(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    context = {
        'project': project,
        'is_member': request.user in project.collaborators.all() or request.user == project.user,
        'pending_requests': [],
    }
    
    # Add pending requests if user is project owner
    if request.user == project.user:
        context['pending_requests'] = ProjectJoinRequest.objects.filter(
            project=project,
            status='pending'
        )
    
    # Check if current user has a pending request
    if request.user != project.user:
        context['join_request_status'] = ProjectJoinRequest.objects.filter(
            project=project,
            user=request.user,
            status='pending'
        ).exists()
    
    return render(request, 'project_info.html', context)

@login_required
def request_to_join(request, project_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid method'}, status=400)
        
    project = get_object_or_404(Project, id=project_id)
    
    # Check if user is already a member
    if request.user in project.collaborators.all() or project.user == request.user:
        return JsonResponse({'error': 'Already a member'}, status=400)
        
    # Check for existing pending request
    existing_request = ProjectJoinRequest.objects.filter(
        project=project,
        user=request.user,
        status='pending'
    ).exists()
    
    if existing_request:
        return JsonResponse({'error': 'Request already pending'}, status=400)
        
    # Create new request
    ProjectJoinRequest.objects.create(
        project=project,
        user=request.user
    )
    
    return JsonResponse({'status': 'success'})

