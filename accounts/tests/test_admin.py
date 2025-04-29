import datetime
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.contrib.admin.sites import AdminSite

from accounts.models import CustomUser, PremierLeagueReferee
from accounts.admin import CustomUserAdmin, PremierLeagueRefereeAdmin

User = get_user_model()


class MockRequest:
    """Mock request for testing admin methods"""
    def __init__(self, user=None):
        self.user = user


class CustomUserAdminTests(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.admin = CustomUserAdmin(CustomUser, self.site)
        
        # Create a superuser for admin access
        self.superuser = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123'
        )
        
        # Create test users
        self.referee = User.objects.create_user(
            username='testreferee',
            email='referee@example.com',
            password='referee123',
            user_type='referee',
            is_approved=False,
            profile_picture_approved=False
        )
        
        self.normal_user = User.objects.create_user(
            username='normaluser',
            email='user@example.com',
            password='user123',
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
        
        # Admin client
        self.client = Client()
        self.client.login(username='admin', password='admin123')
        
        # Admin URLs
        self.admin_url = reverse('admin:accounts_customuser_changelist')
    
    def test_approve_picture_action(self):
        """Test the approve_picture admin action"""
        # Use the action directly
        queryset = CustomUser.objects.filter(username='testreferee')
        self.admin.approve_picture(MockRequest(self.superuser), queryset)
        
        # Check that picture is now approved
        self.referee.refresh_from_db()
        self.assertTrue(self.referee.profile_picture_approved)
    
    def test_approve_referees_action(self):
        """Test the approve_referees admin action"""
        # Use the action directly
        queryset = CustomUser.objects.filter(username='testreferee')
        self.admin.approve_referees(MockRequest(self.superuser), queryset)
        
        # Check that referee is now approved
        self.referee.refresh_from_db()
        self.assertTrue(self.referee.is_approved)
    
    def test_ban_users_action(self):
        """Test the ban_users admin action"""
        # Use the action directly
        queryset = CustomUser.objects.filter(username='normaluser')
        self.admin.ban_users(MockRequest(self.superuser), queryset)
        
        # Check that user is now banned
        self.normal_user.refresh_from_db()
        self.assertTrue(self.normal_user.is_banned)
    
    def test_unban_users_action(self):
        """Test the unban_users admin action"""
        # Use the action directly
        queryset = CustomUser.objects.filter(username='banneduser')
        self.admin.unban_users(MockRequest(self.superuser), queryset)
        
        # Check that user is now unbanned
        self.banned_user.refresh_from_db()
        self.assertFalse(self.banned_user.is_banned)
        self.assertIsNone(self.banned_user.ban_reason)
        self.assertIsNone(self.banned_user.ban_until)
    
    def test_list_display_fields(self):
        """Test the list_display fields in the admin"""
        # Check that list_display includes the required fields
        self.assertIn('username', self.admin.list_display)
        self.assertIn('email', self.admin.list_display)
        self.assertIn('user_type', self.admin.list_display)
        self.assertIn('is_staff', self.admin.list_display)
        self.assertIn('profile_picture_approved', self.admin.list_display)
        self.assertIn('is_approved', self.admin.list_display)
        self.assertIn('is_banned', self.admin.list_display)
    
    def test_list_editable_fields(self):
        """Test the list_editable fields in the admin"""
        # Check that list_editable includes the required fields
        self.assertIn('profile_picture_approved', self.admin.list_editable)
        self.assertIn('is_banned', self.admin.list_editable)
    
    def test_admin_fieldsets(self):
        """Test the admin fieldsets configuration"""
        # Check that our custom fields are included in fieldsets
        custom_fields = None
        for fieldset in self.admin.fieldsets:
            if fieldset[0] == 'Custom Fields':
                custom_fields = fieldset[1]['fields']
                break
        
        self.assertIsNotNone(custom_fields)
        self.assertIn('user_type', custom_fields)
        self.assertIn('fa_certificate_id', custom_fields)
        self.assertIn('bio', custom_fields)
        self.assertIn('profile_picture', custom_fields)
        self.assertIn('profile_picture_approved', custom_fields)
        self.assertIn('is_approved', custom_fields)
        self.assertIn('is_banned', custom_fields)
    
    def test_get_queryset_for_superuser(self):
        """Test the get_queryset method for superusers"""
        # Superuser should see all users
        queryset = self.admin.get_queryset(MockRequest(self.superuser))
        self.assertEqual(queryset.count(), 4)  # All 4 users
    
    def test_get_fieldsets_for_referee(self):
        """Test the get_fieldsets method for referee users"""
        # Should include is_approved for referees
        fieldsets = self.admin.get_fieldsets(MockRequest(self.superuser), self.referee)
        custom_fields = None
        for fieldset in fieldsets:
            if fieldset[0] == 'Custom Fields':
                custom_fields = fieldset[1]['fields']
                break
        
        self.assertIsNotNone(custom_fields)
        self.assertIn('is_approved', custom_fields)
    
    def test_get_fieldsets_for_normal_user(self):
        """Test the get_fieldsets method for normal users"""
        # Should not include is_approved for normal users
        fieldsets = self.admin.get_fieldsets(MockRequest(self.superuser), self.normal_user)
        custom_fields = None
        for fieldset in fieldsets:
            if fieldset[0] == 'Custom Fields':
                custom_fields = fieldset[1]['fields']
                break
        
        self.assertIsNotNone(custom_fields)
        self.assertNotIn('is_approved', custom_fields)
    
    def test_get_inline_instances_for_referee(self):
        """Test the get_inline_instances method for referee users"""
        # Should have PremierLeagueRefereeInline for referees