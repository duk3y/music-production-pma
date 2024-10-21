from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from users.models import Project  

class GoogleOAuthRedirectionTestCase(TestCase):
    def test_oauth_redirection(self):
        # access the project creation page without being logged in
        response = self.client.get(reverse('create_project'))
        
        # ensure user is redirected to Google OAuth login
        self.assertRedirects(response, reverse('socialaccount_login', args=['google']))
