from django.test import TestCase
from django.urls import reverse
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp
from django.test import override_settings

@override_settings(SITE_ID=1)  # Force SITE_ID to 1 during the test
class GoogleOAuthRedirectionTestCase(TestCase):

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

        # Check if the user is redirected to the Google OAuth login page
        self.assertRedirects(response, '/accounts/google/login/?next=/create-project/')