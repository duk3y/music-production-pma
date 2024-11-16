from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    pmaStatus = models.BooleanField(default=False)

class Project(models.Model):
    name = models.CharField(max_length=255, unique=True)
    last_modified = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    collaborators = models.ManyToManyField(User, related_name='collaborating_projects', blank=True)  

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
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='comments')
    timestamp = models.FloatField()  # Stores the timestamp in seconds
    text = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  # Optional: user who added the comment

    def __str__(self):
        return f"{self.project.name} - {self.timestamp}s: {self.text[:20]}"

    # Limit comments to the last 100 for each project
@receiver(post_save, sender=Comment)
def limit_project_comments(sender, instance, **kwargs):
    project = instance.project
    comments = Comment.objects.filter(project=project).order_by('-timestamp')
    if comments.count() > 100:
        for comment in comments[100:]:  # Keep only the 100 most recent comments
            comment.delete()