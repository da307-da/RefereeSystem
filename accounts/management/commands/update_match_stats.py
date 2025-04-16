from django.core.management.base import BaseCommand
from accounts.models import Match
from django.conf import settings
import requests
from accounts.views import update_match_stats

import time
from django.utils import timezone
from datetime import datetime

class Command(BaseCommand):
    help = 'Update match statistics (cards, penalties) from the API'

    def add_arguments(self, parser):
        parser.add_argument('--limit', type=int, help='Limit number of matches to process')
        parser.add_argument('--delay', type=float, default=1.0, help='Delay between API calls (seconds)')
        parser.add_argument('--referee', type=str, help='Filter by referee username')

    def handle(self, *args, **options):
        # Define current season date range with timezone awareness
        season_start = datetime(2024, 8, 1, tzinfo=timezone.get_current_timezone())
        season_end = datetime(2025, 5, 31, tzinfo=timezone.get_current_timezone())
        
        # Start with all matches in the current season
        matches = Match.objects.filter(
            match_date__gte=season_start,
            match_date__lte=season_end
        )
        
        # Filter by referee if specified
        referee_filter = options.get('referee')
        if referee_filter:
            matches = matches.filter(match_referee__username=referee_filter)
            self.stdout.write(f"Filtering matches for referee: {referee_filter}")
        
        # Only include matches with referees assigned
        matches = matches.filter(match_referee__isnull=False)
        
        limit = options.get('limit')
        if limit:
            matches = matches[:limit]
        
        self.stdout.write(f"Updating statistics for {matches.count()} matches")
        
        # Group matches by referee for reporting
        referee_stats = {}
        
        success_count = 0
        failed_count = 0
        delay = options.get('delay')
        
        for i, match in enumerate(matches):
            self.stdout.write(f"Processing match {i+1}/{matches.count()}: {match}")
            
            if update_match_stats(match):
                success_count += 1
                
                # Track stats by referee
                referee = match.match_referee
                referee_name = referee.get_full_name() or referee.username
                
                if referee_name not in referee_stats:
                    referee_stats[referee_name] = {
                        'matches': 0,
                        'yellow_cards': 0,
                        'red_cards': 0,
                        'penalties': 0
                    }
                
                referee_stats[referee_name]['matches'] += 1
                referee_stats[referee_name]['yellow_cards'] += match.yellow_cards_home + match.yellow_cards_away
                referee_stats[referee_name]['red_cards'] += match.red_cards_home + match.red_cards_away
                referee_stats[referee_name]['penalties'] += match.penalties_given
            else:
                failed_count += 1
            
            # Add delay to avoid API rate limits
            if i < matches.count() - 1 and delay > 0:
                time.sleep(delay)
        
        # Display summary by referee
        self.stdout.write("\nReferee Statistics Summary:")
        for referee_name, stats in referee_stats.items():
            avg_yellow = stats['yellow_cards'] / stats['matches'] if stats['matches'] > 0 else 0
            avg_red = stats['red_cards'] / stats['matches'] if stats['matches'] > 0 else 0
            avg_penalties = stats['penalties'] / stats['matches'] if stats['matches'] > 0 else 0
            
            self.stdout.write(f"Referee: {referee_name}")
            self.stdout.write(f"  Matches: {stats['matches']}")
            self.stdout.write(f"  Yellow Cards: {stats['yellow_cards']} (Avg: {avg_yellow:.2f} per match)")
            self.stdout.write(f"  Red Cards: {stats['red_cards']} (Avg: {avg_red:.2f} per match)")
            self.stdout.write(f"  Penalties: {stats['penalties']} (Avg: {avg_penalties:.2f} per match)")
            self.stdout.write("  -------------------")
        
        self.stdout.write("\nOverall Summary:")
        self.stdout.write(f"Total matches processed: {matches.count()}")
        self.stdout.write(self.style.SUCCESS(f"Successfully updated: {success_count}"))
        self.stdout.write(self.style.ERROR(f"Failed to update: {failed_count}"))