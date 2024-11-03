from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path('create-project/', views.create_project, name='create_project'),
    path('join-project/', views.join_project, name='join_project'),
    path('audio/<int:file_id>/add_comment/', views.add_comment, name='add_comment'),
    path('audio/<int:file_id>/', views.audio_playback, name='audio_playback'),
    path('files/<int:file_id>/edit/', views.edit_metadata, name='edit_metadata'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)