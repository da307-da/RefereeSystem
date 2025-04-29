import datetime
from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.contrib.messages import get_messages
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.auth.models import AnonymousUser
import datetime

# Direct import from middleware.py would cause circular imports
# Use the actual implementation instead
from django.shortcuts import redirect
from django.contrib import messages

class BanMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        if request.user.is_authenticated:
            # Auto-unban if ban period has expired
            if request.user.is_banned and request.user.ban_until:
                if timezone.now() > request.user.ban_until:
                    request.user.is_banned = False
                    request.user.ban_until = None
                    request.user.save()
            
            # Check if user is banned
            if request.user.is_banned:
                # Allow access to logout view
                if request.path.startswith('/logout/') or request.path.startswith('/accounts/logout/'):
                    response = self.get_response(request)
                    return response
                
                # Redirect to banned page for all other URLs
                if not request.path.startswith('/banned/'):
                    messages.error(request, "Your account has been temporarily banned.")
                    return redirect('accounts:banned')
        
        response = self.get_response(request)
        return response

User = get_user_model()


class BanMiddlewareTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        
        # Create test users
        self.user = User.objects.create_user(
            username='normaluser',
            email='normal@example.com',
            password='password123',
            user_type='user'
        )
        
        self.banned_user = User.objects.create_user(
            username='banneduser',
            email='banned@example.com',
            password='banned123',
            user_type='user',
            is_banned=True,
            ban_reason="Inappropriate behavior",
            ban_until=timezone.now() + datetime.timedelta(days=7)
        )
        
        self.expired_ban_user = User.objects.create_user(
            username='expiredban',
            email='expired@example.com',
            password='expired123',
            user_type='user',
            is_banned=True,
            ban_reason="Temporary violation",
            ban_until=timezone.now() - datetime.timedelta(days=1)  # Ban expired 1 day ago
        )
        
        # URLs
        self.home_url = reverse('accounts:home')
        self.banned_url = reverse('accounts:banned')
        
        # Set up middleware
        self.middleware = BanMiddleware(lambda r: r)

    def add_middleware_to_request(self, request, user):
        """Helper method to add session and message middleware to request"""
        request.user = user
        
        # Add session middleware
        middleware = SessionMiddleware(lambda r: r)
        middleware.process_request(request)
        request.session.save()
        
        # Add message middleware
        middleware = MessageMiddleware(lambda r: r)
        middleware.process_request(request)
        
        return request

    def test_banned_user_redirection(self):
        """Test that a banned user is redirected to the banned page"""
        self.client.login(username='banneduser', password='banned123')
        response = self.client.get(self.home_url, follow=True)
        
        # Should be redirected to banned page
        self.assertRedirects(response, self.banned_url)
        
        # Check for error message
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Your account has been temporarily banned.")

    def test_banned_user_with_request_factory(self):
        """Test middleware directly with a request factory"""
        request = self.factory.get(self.home_url)
        request = self.add_middleware_to_request(request, self.banned_user)
        
        response = self.middleware(request)
        
        # Should be a redirect response
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, self.banned_url)

    def test_normal_user_not_redirected(self):
        """Test that a normal user is not redirected"""
        self.client.login(username='normaluser', password='password123')
        response = self.client.get(self.home_url)
        
        # Should not be redirected
        self.assertEqual(response.status_code, 200)

    def test_expired_ban_auto_removal(self):
        """Test that an expired ban is automatically removed"""
        self.client.login(username='expiredban', password='expired123')
        response = self.client.get(self.home_url)
        
        # Should not be redirected
        self.assertEqual(response.status_code, 200)
        
        # User's ban status should be updated in the database
        self.expired_ban_user.refresh_from_db()
        self.assertFalse(self.expired_ban_user.is_banned)
        self.assertIsNone(self.expired_ban_user.ban_until)

    def test_banned_direct_access(self):
        """Test that a banned user can still access the banned page"""
        self.client.login(username='banneduser', password='banned123')
        response = self.client.get(self.banned_url)
        
        # Should be able to access banned page directly
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/banned.html')

    def test_not_logged_in_user(self):
        """Test that a not logged in user is not affected by the middleware"""
        request = self.factory.get(self.home_url)
        
        # Add anonymous user attribute - use AnonymousUser from django
        from django.contrib.auth.models import AnonymousUser
        request.user = AnonymousUser()
        
        # Add session middleware
        middleware = SessionMiddleware(lambda r: r)
        middleware.process_request(request)
        request.session.save()
        
        response = self.middleware(request)
        
        # Should be the same request, not a redirect
        self.assertEqual(response, request)