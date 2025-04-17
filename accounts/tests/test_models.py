import datetime
from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model
from accounts.models import (
    CustomUser, PremierLeagueReferee, Match, Team, 
    RefereeDecisionVote, RefereePerformanceRating, Vote, ChatMessage
)

User = get_user_model()

class CustomUserModelTests(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123',
            user_type='user'
        )
        
        self.referee = CustomUser.objects.create_user(
            username='testreferee',
            email='referee@example.com',
            password='referee123',
            user_type='referee',
            fa_certificate_id='REF12345',
            nationality='British',
            years_of_experience=5,
            is_current_referee=True,
            is_approved=True
        )
        
        self.ex_referee = CustomUser.objects.create_user(
            username='exreferee',
            email='exreferee@example.com',
            password='exref123',
            user_type='ex_referee',
            fa_certificate_id='EXREF12345',
            nationality='British',
            years_of_experience=10,
            is_current_referee=False,
            career_duration='2010-2020',
            is_approved=True
        )
        
    def test_user_creation(self):
        """Test that users can be created with correct attributes"""
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertEqual(self.user.user_type, 'user')
        self.assertFalse(self.user.is_approved)
        
        self.assertEqual(self.referee.username, 'testreferee')
        self.assertEqual(self.referee.user_type, 'referee')
        self.assertEqual(self.referee.fa_certificate_id, 'REF12345')
        self.assertTrue(self.referee.is_approved)
        self.assertTrue(self.referee.is_current_referee)
        
        self.assertEqual(self.ex_referee.username, 'exreferee')
        self.assertEqual(self.ex_referee.user_type, 'ex_referee')
        self.assertFalse(self.ex_referee.is_current_referee)
        self.assertEqual(self.ex_referee.career_duration, '2010-2020')
    
    def test_user_string_representation(self):
        """Test the string representation of custom user"""
        self.assertEqual(
            str(self.user), 
            f"testuser (User) - ⏳ Pending Approval"
        )

class PremierLeagueRefereeTests(TestCase):
    def setUp(self):
        self.referee = CustomUser.objects.create_user(
            username='premierlgreferee',
            email='plreferee@example.com',
            password='plref123',
            user_type='referee',
            is_approved=True
        )
        
        self.pl_stats = PremierLeagueReferee.objects.create(
            user=self.referee,
            yellow_cards=45,
            red_cards=3,
            penalties_given=5,
            performance_rating=7.8,
            games_officiated=20,
            poor_decisions=12,
            current_season="2024/25"
        )
    
    def test_premier_league_referee_stats(self):
        """Test the PL referee stats model"""
        self.assertEqual(self.pl_stats.user, self.referee)
        self.assertEqual(self.pl_stats.yellow_cards, 45)
        self.assertEqual(self.pl_stats.red_cards, 3)
        self.assertEqual(self.pl_stats.penalties_given, 5)
        self.assertEqual(self.pl_stats.performance_rating, 7.8)
        self.assertEqual(self.pl_stats.games_officiated, 20)
        self.assertEqual(self.pl_stats.poor_decisions, 12)
        self.assertEqual(self.pl_stats.current_season, "2024/25")
    
    def test_per_game_calculations(self):
        """Test the per-game calculation methods"""
        self.assertEqual(self.pl_stats.poor_decisions_per_game(), 0.6)
        self.assertEqual(self.pl_stats.penalties_per_game(), 0.25)
        
        # Test with zero games
        self.pl_stats.games_officiated = 0
        self.pl_stats.save()
        
        self.assertEqual(self.pl_stats.poor_decisions_per_game(), 0)
        self.assertEqual(self.pl_stats.penalties_per_game(), 0)

class MatchModelTests(TestCase):
    def setUp(self):
        self.referee = CustomUser.objects.create_user(
            username='matchreferee',
            email='matchref@example.com',
            password='match123',
            user_type='referee',
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
        
        self.match = Match.objects.create(
            fixture_id=12345,
            home_team=self.home_team,
            away_team=self.away_team,
            match_date=timezone.now() + datetime.timedelta(days=7),
            venue='Test Stadium',
            status='SCHEDULED',
            match_referee=self.referee
        )
    
    def test_match_creation(self):
        """Test the match model creation"""
        self.assertEqual(self.match.fixture_id, 12345)
        self.assertEqual(self.match.home_team, self.home_team)
        self.assertEqual(self.match.away_team, self.away_team)
        self.assertEqual(self.match.venue, 'Test Stadium')
        self.assertEqual(self.match.status, 'SCHEDULED')
        self.assertEqual(self.match.match_referee, self.referee)
    
    def test_match_score_display(self):
        """Test the score display method"""
        # When scores are None
        self.assertEqual(self.match.get_score_display(), "TBD")
        
        # When scores are set
        self.match.home_score = 2
        self.match.away_score = 1
        self.match.save()
        
        self.assertEqual(self.match.get_score_display(), "2 - 1")
    
    def test_match_string_representation(self):
        """Test string representation of Match"""
        expected_date = self.match.match_date.date()
        self.assertEqual(
            str(self.match),
            f"Home FC vs Away United - {expected_date}"
        )

class RefereePerformanceRatingTests(TestCase):
    def setUp(self):
        self.referee = CustomUser.objects.create_user(
            username='ratedreferee',
            email='rated@example.com',
            password='rated123',
            user_type='referee',
            is_approved=True
        )
        
        self.ex_referee = CustomUser.objects.create_user(
            username='ratingexref',
            email='ratingex@example.com',
            password='ratingex123',
            user_type='ex_referee',
            is_approved=True
        )
        
        self.home_team = Team.objects.create(name='Home FC')
        self.away_team = Team.objects.create(name='Away United')
        
        self.match = Match.objects.create(
            fixture_id=54321,
            home_team=self.home_team,
            away_team=self.away_team,
            match_date=timezone.now() - datetime.timedelta(days=1),
            venue='Rating Stadium',
            status='FINISHED',
            match_referee=self.referee,
            home_score=1,
            away_score=1
        )
        
        self.rating = RefereePerformanceRating.objects.create(
            match=self.match,
            ex_referee=self.ex_referee,
            rating_score=7.5,
            feedback="Good performance overall, but missed a potential penalty"
        )
    
    def test_rating_creation(self):
        """Test referee performance rating model"""
        self.assertEqual(self.rating.match, self.match)
        self.assertEqual(self.rating.ex_referee, self.ex_referee)
        self.assertEqual(self.rating.rating_score, 7.5)
        self.assertEqual(
            self.rating.feedback,
            "Good performance overall, but missed a potential penalty"
        )
    
    def test_unique_together_constraint(self):
        """Test that an ex-referee can't rate the same match twice"""
        with self.assertRaises(Exception):
            RefereePerformanceRating.objects.create(
                match=self.match,
                ex_referee=self.ex_referee,
                rating_score=8.0
            )

class BanSystemTests(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='banneduser',
            email='banned@example.com',
            password='banned123',
            user_type='user'
        )
        
    def test_user_ban(self):
        """Test that users can be banned"""
        # Initially not banned
        self.assertFalse(self.user.is_banned)
        self.assertIsNone(self.user.ban_reason)
        self.assertIsNone(self.user.ban_until)
        
        # Ban the user
        ban_until = timezone.now() + datetime.timedelta(days=7)
        self.user.is_banned = True
        self.user.ban_reason = "Inappropriate behavior"
        self.user.ban_until = ban_until
        self.user.save()
        
        # Verify ban
        self.assertTrue(self.user.is_banned)
        self.assertEqual(self.user.ban_reason, "Inappropriate behavior")
        self.assertEqual(self.user.ban_until, ban_until)