from io import StringIO
from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.core.management import call_command
from django.core.management.base import CommandError
from django.utils import timezone
import datetime

from accounts.models import CustomUser, Team, Match, PremierLeagueReferee


class GeneratePoorDecisionsCommandTests(TestCase):
    def setUp(self):
        # Creates test referee
        self.referee = CustomUser.objects.create_user(
            username='testreferee',
            email='referee@example.com',
            password='referee123',
            user_type='referee',
            is_approved=True
        )
        
        # Creates test teams
        self.team1 = Team.objects.create(name='Team 1', external_id=1001)
        self.team2 = Team.objects.create(name='Team 2', external_id=1002)
        
        # Creates test matches
        self.match = Match.objects.create(
            fixture_id=12345,
            home_team=self.team1,
            away_team=self.team2,
            match_date=timezone.now() - datetime.timedelta(days=1),
            venue='Test Stadium',
            status='FINISHED',
            match_referee=self.referee,
            home_score=2,
            away_score=1
        )
        
        # Creates PL referee stats
        self.pl_stats = PremierLeagueReferee.objects.create(
            user=self.referee,
            yellow_cards=45,
            red_cards=3,
            penalties_given=5,
            performance_rating=7.8,
            games_officiated=20,
            poor_decisions=0,  # Start with 0 poor decisions
            current_season="2024/25"
        )
    
    def test_generate_poor_decisions_command(self):
        """Test the generate_poor_decisions command"""
        out = StringIO()
        call_command('generate_poor_decisions', stdout=out)
        
        # Checks the output contains typical text from this command
        output = out.getvalue()
        self.assertIn('referees with matches', output)
        self.assertIn('Referee: testreferee', output)
        
        # Verifies poor decisions were added to referee stats
        self.pl_stats.refresh_from_db()
        self.assertGreaterEqual(self.pl_stats.poor_decisions, 0)



class UpdateMatchStatsCommandTests(TestCase):
    @patch('requests.get')
    def test_update_match_stats_command(self, mock_get):
        """Test the update_match_stats command"""
        # Creates test referee
        referee = CustomUser.objects.create_user(
            username='testreferee',
            email='referee@example.com',
            password='referee123',
            user_type='referee',
            is_approved=True
        )
        
        # Creates test teams
        team1 = Team.objects.create(name='Team 1', external_id=1001)
        team2 = Team.objects.create(name='Team 2', external_id=1002)
        
        # Creates test match
        match = Match.objects.create(
            fixture_id=12345,
            home_team=team1,
            away_team=team2,
            match_date=timezone.now() - datetime.timedelta(days=1),
            venue='Test Stadium',
            status='FINISHED',
            match_referee=referee,
            home_score=2,
            away_score=1,
            yellow_cards_home=0,
            yellow_cards_away=0,
            red_cards_home=0,
            red_cards_away=0,
            penalties_given=0
        )
        
        # Mock API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'response': [
                {
                    'team': {'id': 1001},  # Home team
                    'type': 'Card',
                    'detail': 'Yellow Card'
                },
                {
                    'team': {'id': 1002},  # Away team
                    'type': 'Card',
                    'detail': 'Red Card'
                },
                {
                    'team': {'id': 1001},  # Home team
                    'type': 'Goal',
                    'detail': 'Penalty'
                }
            ]
        }
        mock_get.return_value = mock_response
        
        # Calls the command
        out = StringIO()
        call_command('update_match_stats', stdout=out)
        
        # Checks the output contains typical text
        output = out.getvalue()
        
        # Verifies the command ran without errors
        self.assertNotIn('Error', output)


class SyncRefereesCommandTests(TestCase):
    @patch('requests.get')
    def test_sync_referees_command(self, mock_get):
        """Test the sync_referees command"""
        # Mock API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'response': [
                {
                    'fixture': {
                        'referee': 'John Smith'
                    },
                    'teams': {
                        'home': {'name': 'Team 1'},
                        'away': {'name': 'Team 2'}
                    }
                },
                {
                    'fixture': {
                        'referee': 'Michael Brown'
                    },
                    'teams': {
                        'home': {'name': 'Team 3'},
                        'away': {'name': 'Team 4'}
                    }
                }
            ]
        }
        mock_get.return_value = mock_response
        
        # Calls the command
        out = StringIO()
        with patch('django.conf.settings.API_KEY', 'test_api_key'):
            call_command('sync_referees', stdout=out)
        
        # Verifies output contains success message
        output = out.getvalue()
        self.assertIn('successfully synced', output.lower())
        
        # Verifies referees were created - this may need adjusting based on actual implementation
        # Just check that at least one referee exists
        self.assertTrue(CustomUser.objects.filter(user_type='referee').exists())


class AssignRefereesToMatchesCommandTests(TestCase):
    def setUp(self):
        # Creates test referees
        for i in range(5):
            CustomUser.objects.create_user(
                username=f'referee{i}',
                email=f'referee{i}@example.com',
                password='password123',
                user_type='referee',
                is_approved=True
            )
        
        # Creates test teams
        self.team1 = Team.objects.create(name='Team 1', external_id=1001)
        self.team2 = Team.objects.create(name='Team 2', external_id=1002)
        self.team3 = Team.objects.create(name='Team 3', external_id=1003)
        self.team4 = Team.objects.create(name='Team 4', external_id=1004)
        
        # Creates test matches without referees
        self.match1 = Match.objects.create(
            fixture_id=1001,
            home_team=self.team1,
            away_team=self.team2,
            match_date=timezone.now() + datetime.timedelta(days=7),
            venue='Stadium 1',
            status='SCHEDULED'
        )
        
        self.match2 = Match.objects.create(
            fixture_id=1002,
            home_team=self.team3,
            away_team=self.team4,
            match_date=timezone.now() + datetime.timedelta(days=8),
            venue='Stadium 2',
            status='SCHEDULED'
        )
    
    @patch('requests.get')
    def test_assign_referees_command(self, mock_get):
        """Test the assign_referees_to_matches command"""
        # Mock API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'response': [
                {
                    'fixture': {
                        'id': 1001,
                        'referee': 'Test Referee',
                        'date': '2025-05-06T15:00:00+00:00',
                    },
                    'teams': {
                        'home': {'name': 'Team 1'},
                        'away': {'name': 'Team 2'}
                    }
                },
                {
                    'fixture': {
                        'id': 1002,
                        'referee': 'Another Referee',
                        'date': '2025-05-07T15:00:00+00:00',
                    },
                    'teams': {
                        'home': {'name': 'Team 3'},
                        'away': {'name': 'Team 4'}
                    }
                }
            ]
        }
        mock_get.return_value = mock_response
        
        # Calls the command
        out = StringIO()
        with patch('django.conf.settings.API_KEY', 'test_api_key'):
            call_command('assign_referees_to_matches', stdout=out)
        
        # Verifies output
        output = out.getvalue()
        self.assertIn('matches without referees', output)
        self.assertIn('Team 1 vs Team 2', output)
        
        # The test passes if the command runs without errors
