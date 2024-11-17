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

@override_settings(
    SITE_ID=1,
    STATICFILES_STORAGE='django.contrib.staticfiles.storage.StaticFilesStorage',
    STATIC_URL='/static/',
    STATIC_ROOT=os.path.join(settings.BASE_DIR, 'staticfiles'),
    STATICFILES_DIRS=[os.path.join(settings.BASE_DIR, 'static')]
)
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
        
        # Check the initial redirect status code and URL
        self.assertEqual(response.status_code, 302)
        expected_url = '/accounts/google/login/?next=/create-project/'
        self.assertTrue(
            response.url.endswith(expected_url),
            f"Expected URL to end with {expected_url}, got {response.url}"
        )