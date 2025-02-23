from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    pmaStatus = models.BooleanField(default=False)

class Project(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)  
    last_modified = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    collaborators = models.ManyToManyField(User, related_name='collaborating_projects', blank=True)
    is_private = models.BooleanField(default=False)  
    password = models.CharField(max_length=128, blank=True, null=True) 

    def __str__(self):
        return self.name

class ProjectFiles(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    file = models.FileField(upload_to='')
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    audio_file = models.FileField(upload_to='uploads/')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    keywords = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.file.name} ({self.project.name})"

class Comment(models.Model):
    file = models.ForeignKey(ProjectFiles, on_delete=models.CASCADE, related_name='comments', null=True)
    timestamp = models.FloatField()
    text = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.timestamp}s: {self.text[:20]}"
    
class Task(models.Model):
    status_options = [('to do','To Do'),('in progress','In Progress'),('waiting approval', 'Waiting Approval'),('done','Done')]
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name = "project_tasks")
    name = models.TextField(max_length=30, blank=False, null=False, default="Default Value")
    status = models.TextField(choices=status_options, default='to do', null=False)
    description = models.TextField(blank=True, null=True)
    deadline = models.DateTimeField()
    assignees = models.ManyToManyField(User, related_name = 'assignees', blank=False)
    created_at = models.DateTimeField(auto_now_add=True)

class DiscussionComment(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='discussion_comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.project.name}: {self.text[:20]}"
    
class ProjectJoinRequest(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='join_requests')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('project', 'user')  # Prevents duplicate requests
        
    def __str__(self):
        return f"{self.user.username} -> {self.project.name} ({self.status})"
