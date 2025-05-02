from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import FileExtensionValidator, MinValueValidator, MaxValueValidator
from django.conf import settings
from django.utils import timezone

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES= (
       ('admin', 'Admin'), 
       ('referee', 'Referee'),
       ('ex_referee', 'Ex-Referee'), 
       ('user', 'User'),
   )
    
    fa_certificate_id = models.CharField(max_length=100, unique=True, blank=True, null=True, verbose_name="FA Referee Course Certificate ID")
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='user')
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', ])], default='profile_pics/default-profile.png'
)
    #field for profile picture approval
    profile_picture_approved = models.BooleanField(default=False)

    nationality = models.CharField(max_length=100, blank=True, null=True)
    years_of_experience = models.PositiveIntegerField(blank=True, null=True)
    is_current_referee = models.BooleanField(default=True)  # True for current, False for ex-referee
    career_duration = models.CharField(max_length=50, blank=True, null=True)  # Only for ex-referees
    age = models.PositiveIntegerField(blank=True, null=True)

    # Admin approval field
    is_approved = models.BooleanField(default=False, verbose_name="Approved by Admin")
    is_banned = models.BooleanField(default=False, verbose_name="Temporarily Banned")
    ban_reason = models.TextField(blank=True, null=True, verbose_name="Ban Reason")
    ban_until = models.DateTimeField(blank=True, null=True, verbose_name="Banned Until")

    # Field used to track registration progress
    registration_complete = models.BooleanField(default=False, verbose_name="Registration Complete")

    def __str__(self):
        approval_status = "✅ Approved" if self.profile_picture_approved else "⏳ Pending Approval"
        return f"{self.username} ({self.get_user_type_display()}) - {approval_status}"
    
class PremierLeagueReferee(models.Model):
    """
    Model to store statistics for Premier League referees.
    """
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='pl_stats')
    yellow_cards = models.PositiveIntegerField(default=0)
    red_cards = models.PositiveIntegerField(default=0)
    penalties_given = models.PositiveIntegerField(default=0)
    performance_rating = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        default=0
    )
    games_officiated = models.PositiveIntegerField(default=0)
    poor_decisions = models.PositiveIntegerField(default=0)
    current_season = models.CharField(max_length=9, default="2024/25")  # Tracks stats by season

    class Meta:
        ordering = ['poor_decisions', '-performance_rating']

    def poor_decisions_per_game(self):
        """
        Calculate the average number of poor decisions per game.
        """
        if self.games_officiated == 0:
            return 0
        return round(self.poor_decisions / self.games_officiated, 2)

    def penalties_per_game(self):
        """
        Calculate the average number of penalties given per game.
        """
        if self.games_officiated == 0:
            return 0
        return round(self.penalties_given / self.games_officiated, 2)

    def __str__(self):
        """
        String representation of the referee.
        """
        return f"{self.user.username} - Season {self.current_season}"
    
class Vote(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    choice = models.CharField(max_length=3)  # 'yes' or 'no'
    created_at = models.DateTimeField(auto_now_add=True)
    match_id = models.IntegerField(default=1) 


    class Meta:
        unique_together = ['user', 'match_id']  # One vote per user

    
class ChatMessage(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='chat_messages')
    content = models.TextField(blank=True, null=True)
    audio_message = models.FileField(
        upload_to='chat_audio/',
        null=True,
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['wav', 'mp3', 'ogg'])]
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.user.username} - {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
    

class Team(models.Model):
    name = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='team_logos/', null=True, blank=True)
    external_id = models.IntegerField(unique=True, blank=True, null=True)  

    def __str__(self):
        return self.name

class Match(models.Model):
    MATCH_STATUS = (
        ('SCHEDULED', 'Scheduled'),
        ('LIVE', 'Live'),
        ('FINISHED', 'Finished'),
    )

    fixture_id = models.IntegerField(unique=True, null=True, blank=True)  # External API Match ID


    home_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='home_matches')
    away_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='away_matches')
    match_date = models.DateTimeField()
    venue = models.CharField(max_length=200)
    home_score = models.IntegerField(null=True, blank=True)
    away_score = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=MATCH_STATUS, default='SCHEDULED')
    red_cards_away = models.PositiveIntegerField(default=0)
    red_cards_home = models.PositiveIntegerField(default=0)
    yellow_cards_away = models.PositiveIntegerField(default=0)
    yellow_cards_home = models.PositiveIntegerField(default=0)
    penalties_given = models.PositiveIntegerField(default=0)


    # Referee fields
    match_referee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='matches_officiated',
        limit_choices_to={'user_type': 'referee'}  # Only allows referee type users
    )

    # Fields for decision analysis
    referee_decision_correct = models.BooleanField(null=True, blank=True)
    decision_votes_correct = models.IntegerField(default=0)
    decision_votes_incorrect = models.IntegerField(default=0)


    decision_description = models.TextField(blank=True, null=True)
    decision_timestamp = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['match_date']

    def __str__(self):
        return f"{self.home_team} vs {self.away_team} - {self.match_date.date()}"
    
    def get_score_display(self):
        """Returns formatted score"""
        if self.home_score is not None and self.away_score is not None:
            return f"{self.home_score} - {self.away_score}"
        return "TBD"
        
    def average_performance_rating(self):
        """Calculates the average performance rating for the referee in this match"""
        ratings = self.referee_ratings.all()
        if not ratings:
            return None
        return sum(rating.rating_score for rating in ratings) / ratings.count()

class RefereeDecisionVote(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='decision_votes')
    voter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    vote = models.BooleanField()  # True for correct, False for incorrect
    timestamp = models.DateTimeField(auto_now_add=True)
    comment = models.TextField(blank=True, null=True)

    class Meta:
        # Ensures one vote per user per match
        unique_together = ['match', 'voter']

    def __str__(self):
        return f"Vote by {self.voter.username} on {self.match}"
    
class RefereePerformanceRating(models.Model):
    """
    Model to store ex-referee ratings for referee performances in specific matches
    """
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='referee_ratings')
    ex_referee = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='given_ratings',
        limit_choices_to={'user_type': 'ex_referee'}
    )
    rating_score = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        help_text="Rate the referee's performance from 0 to 10"
    )
    feedback = models.TextField(blank=True, null=True, help_text="Provide detailed feedback on the referee's performance")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['match', 'ex_referee']  # One rating per ex-referee per match
        ordering = ['-created_at']
        
    def __str__(self):
        return f"Rating for {self.match.match_referee} by {self.ex_referee.username} ({self.rating_score}/10)"
    

class MatchQuestion(models.Model):
    match = models.ForeignKey('Match', on_delete=models.CASCADE, related_name='verification_questions')
    question = models.CharField(max_length=255)
    correct_answer = models.CharField(max_length=255)
    
    
    CATEGORY_CHOICES = (
        ('referee_action', 'Referee Action'),
        ('var_incident', 'VAR Incident'),
        ('broadcast', 'Broadcast Detail'),
        ('visual_element', 'Visual Element'),
        ('sequence', 'Event Sequence'),
        ('environment', 'Match Environment'),
    )
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='referee_action')
    difficulty = models.IntegerField(default=1, choices=[(1, 'Easy'), (2, 'Medium'), (3, 'Hard')])
    
    # Tracks effectiveness of questions
    times_asked = models.IntegerField(default=0)
    times_answered_correctly = models.IntegerField(default=0)
    
    class Meta:
        unique_together = ['match', 'question']  # Prevent duplicate questions
    
    def __str__(self):
        return f"Q for {self.match}: {self.question[:30]}..."
    
    @property
    def effectiveness(self):
        """Calculate question effectiveness (% of correct answers)"""
        if self.times_asked == 0:
            return 0
        return (self.times_answered_correctly / self.times_asked) * 100

class MatchViewingVerification(models.Model):
    """
    Model to track whether a user has verified watching a particular match
    through a quiz or other verification method before rating a referee.
    """
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='match_verifications')
    match = models.ForeignKey('Match', on_delete=models.CASCADE, related_name='viewing_verifications')
    verified = models.BooleanField(default=False)
    verification_timestamp = models.DateTimeField(null=True, blank=True)
    
    # Tracks verification method
    VERIFICATION_METHODS = (
        ('quiz', 'Knowledge Quiz'),
        ('declaration', 'Viewing Declaration'),
        ('clips', 'Key Clips Viewing'),
        ('admin', 'Admin Override'),
    )
    verification_method = models.CharField(max_length=20, choices=VERIFICATION_METHODS, default='quiz')
    
    # Tracks verification details
    verification_score = models.IntegerField(null=True, blank=True)  # For quiz: number of correct answers
    verification_attempts = models.IntegerField(default=1)  # Number of attempts
    

    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'match']
        verbose_name = "Match Viewing Verification"
        verbose_name_plural = "Match Viewing Verifications"
        ordering = ['-verification_timestamp']
    
    def __str__(self):
        verification_status = "Verified" if self.verified else "Not Verified"
        return f"{self.user.username} - {self.match} - {verification_status}"
    
    def save(self, *args, **kwargs):
        # If being marked as verified, set timestamp
        if self.verified and not self.verification_timestamp:
            self.verification_timestamp = timezone.now()
        super().save(*args, **kwargs)
    
    @property
    def is_expired(self):
        """Return True if the verification has expired (e.g., after 48 hours)"""
        if not self.verified or not self.verification_timestamp:
            return True
            
        expiry_period = timezone.timedelta(hours=48)
        return timezone.now() > (self.verification_timestamp + expiry_period)