from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
import datetime
import json
from unittest.mock import patch, MagicMock

from accounts.models import (
    CustomUser, PremierLeagueReferee, Match, Team, 
    RefereeDecisionVote, RefereePerformanceRating, Vote, ChatMessage
)

User = get_user_model()

class HomeViewTests(TestCase):
    @patch('accounts.views.requests.get')
    def test_home_view_with_no_api_data(self, mock_get):
        """Test home page loads when API fails"""
        # Mock API response failure
        mock_get.side_effect = Exception("API Error")
        
        # Access the home page
        response = self.client.get(reverse('accounts:home'))
        
        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/home.html')
        self.assertContains(response, 'Welcome to Ref IQ')
    
    @patch('accounts.views.requests.get')
    def test_home_view_with_api_data(self, mock_get):
        """Test home page with mocked API responses"""

        test_user = User.objects.create_user(
        username='testhomeuser',
        email='testhome@example.com',
        password='testpassword123'
        )
        self.client.login(username='testhomeuser', password='testpassword123')

        # Create mock responses for multiple API calls
        mock_responses = {
            'current_round': MagicMock(
                status_code=200,
                json=lambda: {'response': ['Regular Season - 1']}
            ),
            'all_rounds': MagicMock(
                status_code=200,
                json=lambda: {'response': ['Regular Season - 1', 'Regular Season - 2']}
            ),
            'fixtures': MagicMock(
                status_code=200,
                json=lambda: {'response': [
                    {
                        'fixture': {
                            'id': 1234,
                            'date': '2025-04-16T15:00:00+00:00',
                            'venue': {'name': 'Test Stadium'},
                            'status': {'long': 'Match Finished', 'elapsed': 90}
                        },
                        'teams': {
                            'home': {'name': 'Liverpool', 'logo': 'http://example.com/logo1.png'},
                            'away': {'name': 'Man City', 'logo': 'http://example.com/logo2.png'}
                        },
                        'goals': {'home': 2, 'away': 1}
                    }
                ]}
            ),
            'standings': MagicMock(
                status_code=200,
                json=lambda: {'response': [
                    {
                        'league': {
                            'standings': [
                                [
                                    {
                                        'rank': 1,
                                        'team': {'name': 'Liverpool', 'logo': 'http://example.com/logo1.png'},
                                        'points': 80,
                                        'goalsDiff': 45,
                                        'all': {
                                            'played': 30,
                                            'win': 25,
                                            'draw': 5,
                                            'lose': 0,
                                            'goals': {'for': 70, 'against': 25}
                                        }
                                    }
                                ]
                            ]
                        }
                    }
                ]}
            ),
            'live': MagicMock(
                status_code=200,
                json=lambda: {'response': []}  # No live matches
            )
        }
        
        # Configure mock to return different responses based on URL
        def mock_api_get(url, *args, **kwargs):
            if 'rounds?current=true' in url:
                return mock_responses['current_round']
            elif 'rounds?league=' in url:
                return mock_responses['all_rounds']
            elif 'fixtures?league=' in url:
                return mock_responses['fixtures']
            elif 'standings?league=' in url:
                return mock_responses['standings']
            elif 'fixtures?live=all' in url:
                return mock_responses['live']
            else:
                # Default response for other cases
                return MagicMock(status_code=200, json=lambda: {'response': []})
        
        mock_get.side_effect = mock_api_get
        
        # Accesses the home page
        response = self.client.get(reverse('accounts:home'))
        
        # Checks response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/home.html')
        
        # Check that the API data is present in the context
        self.assertTrue('standings' in response.context)
        self.assertTrue('live_matches' in response.context)
        self.assertTrue('past_matches' in response.context)
        
        # Checks specific content on the page
        self.assertContains(response, 'Premier League Table')
        self.assertContains(response, 'Liverpool')  # Team name from standings

class AuthenticationViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.register_referee_url = reverse('accounts:register_referee')
        self.register_user_url = reverse('accounts:register_user')
        self.register_ex_referee_url = reverse('accounts:register_ex_referee')
        self.login_url = reverse('accounts:login')
        self.logout_url = reverse('accounts:logout')
        
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123',
            user_type='user'
        )
        
        # Create a test referee
        self.referee = User.objects.create_user(
            username='testreferee',
            email='referee@example.com',
            password='referee123',
            user_type='referee',
            fa_certificate_id='REF123456',
            is_approved=True
        )
    
    def test_register_user_view_get(self):
        """Test get request to user registration page"""
        response = self.client.get(self.register_user_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/register_user.html')
    
    def test_register_user_view_post(self):
        """Test successful user registration"""
        user_data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password1': 'newpassword123',
            'password2': 'newpassword123',
        }
        response = self.client.post(self.register_user_url, user_data)
        
        # Should redirect to home page on success
        self.assertRedirects(response, reverse('accounts:home'))
        
        # Check that user was created
        self.assertTrue(User.objects.filter(username='newuser').exists())
        new_user = User.objects.get(username='newuser')
        self.assertEqual(new_user.email, 'new@example.com')
        self.assertEqual(new_user.user_type, 'user')
    
    def test_register_referee_view_get(self):
        """Test get request to referee registration page"""
        response = self.client.get(self.register_referee_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/register_referee.html')
    
    def test_register_referee_two_step_process(self):
        """Test the two-step referee registration process"""
        # Step 1: Basic registration
        step1_data = {
            'username': 'newreferee',
            'email': 'newref@example.com',
            'password1': 'newrefpassword123',
            'password2': 'newrefpassword123',
            'fa_certificate_id': 'NEWREF123',
            'step1': 'Next'
        }
        response = self.client.post(self.register_referee_url, step1_data)
        
        # Should redirect to step 2
        self.assertRedirects(response, reverse('accounts:register_referee_step2'))
        
        # Check user was created
        new_ref = User.objects.get(username='newreferee')
        
        self.assertEqual(new_ref.user_type, 'referee')
        self.assertFalse(new_ref.is_approved)
        self.assertFalse(new_ref.registration_complete)
        
        # Step 2: Additional details
        self.client.login(username='newreferee', password='newrefpassword123')
        step2_data = {
            'nationality': 'British',
            'years_of_experience': 5,
            'is_current_referee': True,
            'step2': 'Complete Registration'
        }
        response = self.client.post(reverse('accounts:register_referee_step2'), step2_data)
        
        # Should redirect to pending approval page
        self.assertRedirects(response, reverse('accounts:pending_approval'))
        
        # Refresh user from DB
        new_ref.refresh_from_db()
        self.assertTrue(new_ref.registration_complete)
        self.assertEqual(new_ref.nationality, 'British')
        self.assertEqual(new_ref.years_of_experience, 5)
        self.assertTrue(new_ref.is_current_referee)
    
    def test_login_view(self):
        """Test user login"""
        # Get login page
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/login.html')
        
        # Test successful login
        login_data = {
            'username': 'testuser',
            'password': 'testpassword123'
        }
        response = self.client.post(self.login_url, login_data)
        
        # Should redirect to home
        self.assertRedirects(response, reverse('accounts:home'))
        
        # Test user is logged in
        self.assertTrue(response.wsgi_request.user.is_authenticated)
        self.assertEqual(response.wsgi_request.user.username, 'testuser')
    
    def test_unapproved_referee_login(self):
        """Test that unapproved referees get an error message"""
        # Create unapproved referee
        unapproved_ref = User.objects.create_user(
            username='unapprovedreferee',
            email='unapproved@example.com',
            password='unapproved123',
            user_type='referee',
            is_approved=False
        )
        
        login_data = {
            'username': 'unapprovedreferee',
            'password': 'unapproved123'
        }
        response = self.client.post(self.login_url, login_data, follow=True)
        
        # Should show error message
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Your account is pending admin approval.")
        
        # Should redirect back to login page
        self.assertEqual(response.redirect_chain[0][0], reverse('accounts:login'))
    
    def test_logout_view(self):
        """Test user logout"""
        # First login
        self.client.login(username='testuser', password='testpassword123')
        
        # Then logout
        response = self.client.get(self.logout_url)
        
        # Should redirect to home
        self.assertRedirects(response, reverse('accounts:home'))
        
        # User should be logged out
        user = response.wsgi_request.user
        self.assertFalse(user.is_authenticated)

class RefereePerformanceViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Create users
        self.referee = User.objects.create_user(
            username='activereferee',
            email='active@example.com',
            password='active123',
            user_type='referee',
            is_approved=True,
            is_current_referee=True
        )
        
        self.ex_referee = User.objects.create_user(
            username='exreferee',
            email='ex@example.com',
            password='ex123',
            user_type='ex_referee',
            is_approved=True,
            is_current_referee=False
        )
        
        self.normal_user = User.objects.create_user(
            username='normaluser',
            email='normal@example.com',
            password='normal123',
            user_type='user'
        )
        
        # Create teams
        self.home_team = Team.objects.create(
            name='Chelsea',
            external_id=1001
        )
        
        self.away_team = Team.objects.create(
            name='Arsenal',
            external_id=1002
        )
        
        # Create match
        self.match = Match.objects.create(
            fixture_id=12345,
            home_team=self.home_team,
            away_team=self.away_team,
            match_date=timezone.now() - datetime.timedelta(days=1),
            venue='Stamford Bridge',
            status='FINISHED',
            match_referee=self.referee,
            home_score=2,
            away_score=1,
            yellow_cards_home=2,
            yellow_cards_away=3,
            red_cards_home=0,
            red_cards_away=1,
            penalties_given=1
        )
        
        # URLs
        self.ex_referee_dashboard_url = reverse('accounts:ex_referee_dashboard')
        self.rate_referee_url = reverse('accounts:rate_referee', kwargs={'fixture_id': 12345})
        self.leaderboard_url = reverse('accounts:referee_leaderboard')
        self.my_latest_performance_url = reverse('accounts:my_latest_performance')
        self.most_recent_match_rating_url = reverse('accounts:most_recent_match_rating')
    
    def test_ex_referee_dashboard_access(self):
        """Test that only ex-referees can access the dashboard"""
        # Normal user - should redirect
        self.client.login(username='normaluser', password='normal123')
        response = self.client.get(self.ex_referee_dashboard_url)
        self.assertEqual(response.status_code, 302)  # Redirect
        
        # Referee - should redirect
        self.client.login(username='activereferee', password='active123')
        response = self.client.get(self.ex_referee_dashboard_url)
        self.assertEqual(response.status_code, 302)  # Redirect
        
        # Ex-referee - should have access
        self.client.login(username='exreferee', password='ex123')
        response = self.client.get(self.ex_referee_dashboard_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/ex_referee_dashboard.html')
        
        # Check context data
        self.assertTrue('matches' in response.context)
        self.assertEqual(list(response.context['matches']), [self.match])
    
    def test_rate_referee_as_ex_referee(self):
        """Test rating submission by an ex-referee"""
        self.client.login(username='exreferee', password='ex123')
        
        # Submit rating via POST
        rating_data = {
            'rating': 8.5,
            'feedback': 'Excellent performance, managed the game well'
        }
        response = self.client.post(
            self.rate_referee_url,
            data=json.dumps(rating_data),
            content_type='application/json',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        # Check response
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        
        # Check that rating was created
        self.assertTrue(
            RefereePerformanceRating.objects.filter(
                match=self.match,
                ex_referee=self.ex_referee,
                rating_score=8.5
            ).exists()
        )
    
    def test_rate_referee_as_non_ex_referee(self):
        """Test that non-ex-referees cannot submit ratings"""
        self.client.login(username='normaluser', password='normal123')
        
        # Try to submit rating
        rating_data = {
            'rating': 6.0,
            'feedback': 'Made some questionable calls'
        }
        response = self.client.post(
            self.rate_referee_url,
            data=json.dumps(rating_data),
            content_type='application/json',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        # Should get an error
        self.assertEqual(response.status_code, 403)
        response_data = json.loads(response.content)
        self.assertTrue('error' in response_data)
    
    def test_referee_leaderboard_access(self):
        """Test access to the referee leaderboard"""
        # Anyone should be able to view the leaderboard
        response = self.client.get(self.leaderboard_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/referee_leaderboard.html')
        
        # Check context
        self.assertTrue('leaderboard' in response.context)
        self.assertEqual(response.context['season'], '2024-2025')
    
    def test_my_latest_performance_for_referee(self):
        """Test that a referee can see their latest performance stats"""
        # Create a rating for the match
        rating = RefereePerformanceRating.objects.create(
            match=self.match,
            ex_referee=self.ex_referee,
            rating_score=7.5,
            feedback="Good overall performance"
        )
        
        # Login as referee
        self.client.login(username='activereferee', password='active123')
        
        # Request performance data
        response = self.client.get(self.my_latest_performance_url)
        
        # Check response
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        
        self.assertTrue(response_data['success'])
        self.assertEqual(response_data['match']['home_team']['name'], 'Chelsea')
        self.assertEqual(response_data['match']['away_team']['name'], 'Arsenal')
        self.assertEqual(response_data['match']['home_team']['score'], 2)
        self.assertEqual(response_data['match']['away_team']['score'], 1)
        self.assertEqual(response_data['match']['ratings']['avg_rating'], 7.5)
    
    def test_my_latest_performance_for_non_referee(self):
        """Test that non-referees cannot access this endpoint"""
        self.client.login(username='normaluser', password='normal123')
        
        response = self.client.get(self.my_latest_performance_url)
        
        # Check response
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        
        self.assertFalse(response_data['success'])
        self.assertTrue('message' in response_data)

class BanMiddlewareTests(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Create user
        self.user = User.objects.create_user(
            username='bannableuser',
            email='bannable@example.com',
            password='bannable123',
            user_type='user'
        )
        
        # Login URLs
        self.home_url = reverse('accounts:home')
        self.banned_url = reverse('accounts:banned')