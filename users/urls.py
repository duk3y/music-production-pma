from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    # Project creation and joining
    path('create-project/', views.create_project, name='create_project'),
    path('projects/<int:project_id>/', views.project_info, name='project_info'),  
    path('join-project/', views.join_project, name='join_project_list'),
    path('join-project/<int:project_id>/', views.join_project, name='join_project'),
    path('join-private-project/<int:project_id>/', views.join_private_project, name='join_private_project'),
    path('request/<int:request_id>/accept/', views.accept_request, name='accept_request'),
    path('request/<int:request_id>/ignore/', views.ignore_request, name='ignore_request'),
    
    # Project files and management
    path('project/<int:project_id>/files/', views.project_files, name='project_files'),
    path('files/<int:file_id>/edit/', views.edit_metadata, name='edit_metadata'),
    
    # Audio and comments
    path('audio/<int:file_id>/', views.audio_playback, name='audio_playback'),
    path('audio/<int:file_id>/add_comment/', views.add_comment, name='add_comment'),
    path('comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    
    # Join request management
    path('project/<int:project_id>/request-join/', views.request_to_join, name='request_join'),
    path('project/<int:project_id>/manage-requests/', views.manage_join_requests, name='manage_join_requests'),
    path('join-request/<int:request_id>/<str:action>/', views.handle_join_request, name='handle_join_request'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)