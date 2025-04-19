import datetime
import json
from django.urls import reverse
from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model
from accounts.models import (
    CustomUser, PremierLeagueReferee, Match, Team, 
    RefereeDecisionVote, RefereePerformanceRating, Vote, ChatMessage
)

User = get_user_model()

class FunctionalTestCase(TestCase):
    def setUp(self):

        # Creates test users
        self.user = User.objects.create_user(
            username='normaluser',
            email='user@example.com',
            password='normal123',
            user_type='user'
        )
        
        self.referee = User.objects.create_user(
            username='activereferee',
            email='referee@example.com',
            password='active123',
            user_type='referee',
            is_approved=True
        )
        
        self.ex_referee = User.objects.create_user(
            username='exreferee',
            email='ex@example.com',
            password='ex123',
            user_type='ex_referee',
            is_approved=True
        )

        self.home_team = Team.objects.create(
            name='Home FC',
            external_id=1001
        )
        
        self.away_team = Team.objects.create(
            name='Away United',
            external_id=1002
        )
    
    def _create_test_match_with_referee(self):
        """Helper method to create a test match with referee"""
        match = Match.objects.create(
            fixture_id=12345,
            home_team=self.home_team,
            away_team=self.away_team,
            match_date=timezone.now() - datetime.timedelta(days=1),
            venue='Test Stadium',
            status='FINISHED',
            match_referee=self.referee,
            home_score=2,
            away_score=1
        )
        return match

    def _create_test_match_with_decision(self):
        """Helper method to create a test match with a controversial decision"""
        match = Match.objects.create(
            fixture_id=54321,
            home_team=self.home_team,
            away_team=self.away_team,
            match_date=timezone.now() - datetime.timedelta(days=1),
            venue='Decision Stadium',
            status='FINISHED',
            match_referee=self.referee,
            home_score=1,
            away_score=1,
            referee_decision_correct=None  # Controversial decision
        )
        return match

    def test_full_referee_rating_flow(self):
        """Test the complete flow of an ex-referee rating a referee's performance"""
        # Set up match with a referee
        match = self._create_test_match_with_referee()
        
        # Login as ex-referee
        self.client.login(username='exreferee', password='ex123')
        
        # First, navigate to the ex-referee dashboard
        dashboard_response = self.client.get(reverse('accounts:ex_referee_dashboard'))
        self.assertEqual(dashboard_response.status_code, 200)
        
        # Click on the match to rate
        match_detail_response = self.client.get(reverse('accounts:rate_referee', kwargs={'fixture_id': match.fixture_id}))
        self.assertEqual(match_detail_response.status_code, 200)
        
        # Submit the rating form
        rating_data = {
            'rating_score': 8.5,
            'feedback': 'Good management of the game overall'
        }
        rating_response = self.client.post(
            reverse('accounts:rate_referee', kwargs={'fixture_id': match.fixture_id}),
            rating_data,
            follow=True
        )
        
        # Should be redirected to dashboard with success message
        self.assertRedirects(rating_response, reverse('accounts:ex_referee_dashboard'))
        
        # Verify rating was saved
        self.assertTrue(
            RefereePerformanceRating.objects.filter(
                match=match,
                ex_referee=self.ex_referee,
                rating_score=8.5
            ).exists()
        )
    def test_fan_voting_flow(self):
        """Test a fan voting on a referee's decision"""

        match = self._create_test_match_with_decision()
        

        self.client.login(username='normaluser', password='normal123')
        
        # Navigates to the home page
        home_response = self.client.get(reverse('accounts:home'))
        self.assertEqual(home_response.status_code, 200)
        
        # Submit a vote
        vote_data = {
            'choice': 'yes',
            'match_id': match.fixture_id
        }

        vote_response = self.client.post(
            reverse('accounts:submit_vote'),
            vote_data,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        # Checks JSON response
        self.assertEqual(vote_response.status_code, 200)
        vote_json = json.loads(vote_response.content)
        self.assertTrue('yes' in vote_json)
        self.assertTrue('no' in vote_json)
        
        # Verifies that the vote was saved
        self.assertTrue(
            Vote.objects.filter(
                user__username='normaluser',
                match_id=match.fixture_id,
                choice='yes'
            ).exists()
        )
        
        # Check ability to change vote
        change_vote_data = {
            'choice': 'no',
            'match_id': match.fixture_id
        }

        change_response = self.client.post(
            reverse('accounts:submit_vote'),
            change_vote_data,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        # Verify vote was updated
        self.assertEqual(
            Vote.objects.get(
                user__username='normaluser',
                match_id=match.fixture_id
            ).choice,
            'no'
        )

    
    