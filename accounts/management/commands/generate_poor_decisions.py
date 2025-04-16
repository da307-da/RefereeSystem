from django.core.management.base import BaseCommand
from django.db.models import Count, Avg, F, Sum, Case, When, IntegerField
from accounts.models import CustomUser, Match
import random

class Command(BaseCommand):
    help = 'Generate random poor decision data for referees'

    def handle(self, *args, **kwargs):
        # Get all referees who have officiated matches
        referees = CustomUser.objects.filter(
            user_type='referee',
            matches_officiated__isnull=False
        ).distinct()
        
        self.stdout.write(f"Found {referees.count()} referees with matches")
        
        # For each referee
        for referee in referees:
            # Get all matches officiated by this referee
            matches = Match.objects.filter(match_referee=referee)
            match_count = matches.count()
            
            if match_count == 0:
                continue
                
            # Generate poor decision rate based on quality (higher rated referees make fewer mistakes)
            avg_rating = matches.aggregate(avg=Avg('referee_ratings__rating_score'))['avg'] or 5.0
            
            # Invert the rating scale - higher rated referees have lower error rates
            # Scale from roughly 0.05 (5%) for 10/10 referees to 0.30 (30%) for 0/10 referees
            base_error_rate = 0.30 - (avg_rating / 10 * 0.25)
            
            # Add some randomness (±20% variation)
            error_rate = base_error_rate * random.uniform(0.8, 1.2)
            
            # Calculate expected poor decisions per match
            poor_decisions_per_match = error_rate * 10  # Assuming ~10 major decisions per match
            
            # Calculate total poor decisions
            total_poor_decisions = int(poor_decisions_per_match * match_count)
            
            self.stdout.write(f"Referee: {referee.username}")
            self.stdout.write(f"  Matches: {match_count}")
            self.stdout.write(f"  Avg Rating: {avg_rating:.1f}")
            self.stdout.write(f"  Error Rate: {error_rate:.2f}")
            self.stdout.write(f"  Poor decisions per match: {poor_decisions_per_match:.1f}")
            self.stdout.write(f"  Total poor decisions: {total_poor_decisions}")
            
            # Distribute poor decisions across matches
            remaining_decisions = total_poor_decisions
            processed_matches = 0
            
            for match in matches:
                if processed_matches == match_count - 1:
                    # Last match - assign all remaining decisions
                    match.referee_decisions_incorrect = remaining_decisions
                else:
                    # Randomly assign decisions to this match
                    max_decisions = min(int(poor_decisions_per_match * 2), remaining_decisions)
                    decisions_in_match = random.randint(0, max_decisions)
                    match.referee_decisions_incorrect = decisions_in_match
                    remaining_decisions -= decisions_in_match
                
                match.save()
                processed_matches += 1
            
        self.stdout.write(self.style.SUCCESS('Successfully generated poor decision data'))