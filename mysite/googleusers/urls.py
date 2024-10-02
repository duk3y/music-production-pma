from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Root URL (google/)
    path('google-home/', views.home, name='google_home'),  # Map google-home to home view
    path('logout/', views.logout_view, name='logout'),  # Logout view
]
