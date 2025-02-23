"""
URL configuration for mysite project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path

from . import views
from .views import CustomLoginView, user_tasks, project_files_view, delete_task_project_overview, updateTaskStatus, delete_task, TaskInfoView, CalendarView, CommonDefaultView, ManageFilesAdminView, ManageProjectsAdminView, AuthenticationView, upload_file, login_redirect, ProjectTaskView, create_task


urlpatterns = [
    path('projects/<int:project_id>/tasks/', ProjectTaskView, name='project_task_view'), 
    path('projects/<int:project_id>/tasks/<int:task_id>/info/', TaskInfoView, name='task_info_view'),
    path('projects/<int:project_id>/tasks/upload/', create_task, name = 'task_upload' ),
    path('projects/<int:project_id>/upload/', upload_file, name='file_upload'),
    path('projects/<int:project_id>/tasks/<int:task_id>/delete/', delete_task, name="task_delete"),
    path('file/delete/<int:file_id>/', views.delete_file, name='delete_file'),
    path('task/delete/<int:task_id>/', delete_task_project_overview, name="delete_task_project_overview"),
    path('projects/<int:project_id>/edit/', views.edit_project, name='edit_project'),
    path('projects/<int:project_id>/manage_files/', views.manage_files, name='manage_files'),
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path('', views.home, name='home'),
    path('google/', include('mysite.googleusers.urls'), name='google_login'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('common/', CommonDefaultView.as_view(), name='common_default'),
    path('calendar/', CalendarView, name="calendar_view"),
    path('api/user_tasks/', user_tasks, name="user_tasks_calendar"),
    path('api/status-update/', updateTaskStatus, name='update_task_status'),
    path('manage-files-admin/', ManageFilesAdminView.as_view(), name='manage_files_admin'),
    path("login-post", AuthenticationView, name="authentication_view"),
    path('projects/<int:project_id>/manage-files', project_files_view, name="manage_project_files" ),
    path('', include('users.urls')),  
    path('login-redirect/', login_redirect, name='login_redirect'),
    path('public-projects/', views.public_projects, name='public_projects'),
    path('projects/<int:project_id>/add_comment/', views.add_project_comment, name='add_project_comment'),
    path('projects/comment/<int:comment_id>/resolve/', views.resolve_discussion_comment, name='resolve_discussion_comment'),
    path('projects/<int:project_id>/search/', views.search_files, name='search_files'),
    path('projects/<int:project_id>/delete/', views.delete_project, name='delete_project'),
    path('projects/<int:project_id>/leave/', views.leave_project, name='leave_project'),
    path('projects/<int:project_id>/delete/confirm/', views.confirm_delete_project, name='confirm_delete_project'),
    path('projects/<int:project_id>/leave/confirm/', views.confirm_leave_project, name='confirm_leave_project'),
    path('file/<int:file_id>/manage-delete/', views.delete_file_from_manage, name='delete_file_from_manage'),
    path('pmaadmin/file/delete/<int:file_id>/', views.delete_file_from_admin, name='delete_file_from_admin'),
     path('manage-projects-admin/', ManageProjectsAdminView.as_view(), name='manage_projects_admin'),



]
"""# uncomment these lines if you want to test during development, not needed during production (heroku)
from django.conf import settings
from django.conf.urls.static import static
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)"""