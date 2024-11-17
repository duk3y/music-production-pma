from django.test import TestCase, override_settings
from django.urls import reverse
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp
from django.contrib.auth.models import User
from users.models import Profile, Project
from django.contrib import auth
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.conf import settings
import os

@override_settings(
    STATICFILES_STORAGE='django.contrib.staticfiles.storage.StaticFilesStorage',
    STATIC_URL='/static/',
    STATIC_ROOT=os.path.join(settings.BASE_DIR, 'staticfiles'),
    STATICFILES_DIRS=[os.path.join(settings.BASE_DIR, 'static')]
)
class GoogleOAuthLoginSuccessTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Create necessary directories if they don't exist
        os.makedirs(os.path.join(settings.BASE_DIR, 'static'), exist_ok=True)
        os.makedirs(os.path.join(settings.BASE_DIR, 'staticfiles'), exist_ok=True)
        
        # Create a dummy logo.png if it doesn't exist
        logo_path = os.path.join(settings.BASE_DIR, 'static', 'logo.png')
        if not os.path.exists(logo_path):
            with open(logo_path, 'wb') as f:
                f.write(b'dummy content')

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
        # First, make sure we're logged in
        self.client.login(username='testuser', password='password')
        
        # Then access the create project page
        response = self.client.get(reverse('create_project'))
        
        # Should get a 200 response now
        self.assertEqual(response.status_code, 200)
        
        # Verify we got the create project template
        self.assertTemplateUsed(response, 'createproject.html')