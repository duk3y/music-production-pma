from django.shortcuts import render, redirect

# Create your views here.
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from users.forms import ProjectForm, JoinProjectForm
from django.http import HttpResponseRedirect
from .models import Project
from django.urls import reverse


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
