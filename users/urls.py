from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path('create-project/', views.create_project, name='create_project'),
    path('join-project/', views.join_project, name='join_project_list'),  # Shows the list of projects
    path('join-project/<int:project_id>/', views.join_project, name='join_project'),  # Handles joining a specific project
    path('join-private-project/<int:project_id>/', views.join_private_project, name='join_private_project'),
    path('audio/<int:file_id>/add_comment/', views.add_comment, name='add_comment'),
    path('audio/<int:file_id>/', views.audio_playback, name='audio_playback'),
    path('files/<int:file_id>/edit/', views.edit_metadata, name='edit_metadata'),
    path('comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    path('project/<int:project_id>/files/', views.project_files, name='project_files'),
    path('audio/<int:file_id>/', views.audio_playback, name='audio_playback'),
    path('audio/<int:file_id>/add_comment/', views.add_comment, name='add_comment'),
    path('comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    path('project/<int:project_id>/manage-requests/', views.manage_join_requests, name='manage_join_requests'),
    path('join-request/<int:request_id>/<str:action>/', views.handle_join_request, name='handle_join_request'),
    path('project/<int:project_id>/request-join/', views.request_to_join, name='request_join'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)