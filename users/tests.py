from django.test import TestCase
from django.urls import reverse
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp
from django.test import override_settings
from django.contrib.auth.models import User
from users.models import Profile, Project
from django.contrib import auth
from urllib.parse import urlparse, parse_qs
from django.conf import settings
import os

@override_settings(SITE_ID=1)  # Force SITE_ID to 1 during the test
class GoogleOAuthRedirectionTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Create necessary directories if they don't exist
        os.makedirs(os.path.join(settings.BASE_DIR, 'static'), exist_ok=True)
        os.makedirs(os.path.join(settings.BASE_DIR, 'staticfiles'), exist_ok=True)

    def setUp(self):
        # Create a Site object to associate the SocialApp with
        site, created = Site.objects.update_or_create(
            id=1, defaults={'domain': '127.0.0.1', 'name': 'localhost'}
        )

        # Create a SocialApp object for Google OAuth and associate it with the Site
        google_app = SocialApp.objects.create(
            provider='google',
            name='Google',
            client_id='fake-client-id',
            secret='fake-secret-key'
        )
        google_app.sites.add(site)

    def test_oauth_redirection(self):
        # Access the project creation page without being logged in
        response = self.client.get(reverse('create_project'))
        
        # Just check the initial redirect status code and URL
        self.assertEqual(response.status_code, 302)
        expected_url = '/accounts/google/login/?next=/create-project/'
        self.assertTrue(
            response.url.endswith(expected_url),
            f"Expected URL to end with {expected_url}, got {response.url}"
        )

@override_settings(SITE_ID=1)
class GoogleOAuthLoginSuccessTestCase(TestCase):
    def setUp(self):
        # Create site for OAuth
        site, created = Site.objects.update_or_create(
            id=1, defaults={'domain': '127.0.0.1', 'name': 'localhost'}
        )
        
        # Create Google app
        google_app = SocialApp.objects.create(
            provider='google',
            name='Google',
            client_id='fake-client-id',
            secret='fake-secret-key'
        )
        google_app.sites.add(site)
        
        # Create test user
        self.user = User.objects.create_user(username='testuser', password='password')
        Profile.objects.update_or_create(
            user=self.user,
            defaults={'pmaStatus': False}
        )

    def test_successful_login_redirect(self):
        # Access the create project page without logging in first
        response = self.client.get(reverse('create_project'))
        
        # Should be redirected to login page
        self.assertEqual(response.status_code, 302)
        
        # Parse the redirect URL and its query parameters
        parsed_url = urlparse(response.url)
        query_params = parse_qs(parsed_url.query)
        
        # Verify redirect path and next parameter
        self.assertEqual(parsed_url.path, '/accounts/google/login/')
        self.assertEqual(query_params.get('next', [None])[0], '/create-project/')
        
        # Now login
        login_successful = self.client.login(username='testuser', password='password')
        self.assertTrue(login_successful, "Login failed")
        
        # Access create project page again after login
        response = self.client.get(reverse('create_project'))
        
        # Now should get a 200 response
        self.assertEqual(response.status_code, 200)
        
        # Verify we got the create project template
        self.assertTemplateUsed(response, 'createproject.html')

class CommonDefaultViewTestCase(TestCase):
    def setUp(self):
        # Create a user for testing
        self.user = User.objects.create_user(username='testuser', password='password')
        
        # Create or update profile
        Profile.objects.update_or_create(user=self.user, defaults={'pmaStatus': False})

        # Create projects owned by the user
        self.owned_project1 = Project.objects.create(name="Owned Project 1", user=self.user)
        self.owned_project2 = Project.objects.create(name="Owned Project 2", user=self.user)

        # Create another user and a project where testuser is a collaborator
        self.collaborator = User.objects.create_user(username='collaborator', password='password')
        self.collaborating_project = Project.objects.create(name="Collaborating Project", user=self.collaborator)
        self.collaborating_project.collaborators.add(self.user)

    @override_settings(STATICFILES_STORAGE='django.contrib.staticfiles.storage.StaticFilesStorage')
    def test_own_and_collaborating_projects(self):
        # Log in the user
        login_successful = self.client.login(username='testuser', password='password')
        self.assertTrue(login_successful, "Login failed")

        # Verify user is authenticated
        user = auth.get_user(self.client)
        self.assertTrue(user.is_authenticated, "User is not authenticated")

        # Access the view
        response = self.client.get(reverse('common_default'))
        self.assertEqual(response.status_code, 200)

        # Verify that the correct projects are in the context
        self.assertIn(self.owned_project1, response.context['projects'])
        self.assertIn(self.owned_project2, response.context['projects'])
        self.assertIn(self.collaborating_project, response.context['projects'])

        # Ensure there are no duplicate projects
        self.assertEqual(len(response.context['projects']), 3)