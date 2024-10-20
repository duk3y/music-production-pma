from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path('create-project/', views.create_project, name='create_project'),
    path('join-project/', views.join_project, name='join_project'),
]