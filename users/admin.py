from django.contrib import admin
from .models import Profile, Project, ProjectFiles, Comment


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'pmaStatus')

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'last_modified', 'user')

@admin.register(ProjectFiles)
class PProjectFilesAdmin(admin.ModelAdmin):
    list_display = ('project', 'file', 'uploaded_by', 'created_at')

admin.site.register(Comment)
