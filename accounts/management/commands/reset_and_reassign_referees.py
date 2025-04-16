from django.core.management.base import BaseCommand
from accounts.models import Match
from django.utils import timezone
from datetime import datetime
import requests
from django.conf import settings
from accounts.views import sync_referee_to_database
import time

class Command(BaseCommand):
    help = 'Unassign and then reassign referees to matches'

    def add_arguments(self, parser):
        parser.add_argument('--limit', type=int, help='Limit number of matches to process')
        parser.add_argument('--delay', type=float, default=1.0, help='Delay between API calls (seconds)')

    def handle(self, *args, **options):
        # Define current season date range
        season_start = timezone.make_aware(
            datetime(2024, 8, 1), 
            timezone=timezone.get_default_timezone()
        )
        season_end = timezone.make_aware(
            datetime(2025, 5, 31), 
            timezone=timezone.get_default_timezone()
        )
        
        # Step 1: Unassign referees
        matches = Match.objects.filter(
            match_referee__isnull=False,
            match_date__gte=season_start,
            match_date__lte=season_end
        )
        
        total = matches.count()
        self.stdout.write(f"Found {total} matches with referees to unassign")
        
        # Apply limit if specified
        limit = options.get('limit')
        if limit:
            matches = matches[:limit]
            self.stdout.write(f"Processing first {limit} matches")
        
        # Unassign referees
        for match in matches:
            match.match_referee = None
            match.save()
        
        self.stdout.write(self.style.SUCCESS(f"Unassigned referees from {len(matches)} matches"))
        
        # Step 2: Reassign referees (similar to your original script)
        matches_without_referee = Match.objects.filter(
            match_referee=None,
            match_date__gte=season_start,
            match_date__lte=season_end
        )
        
        delay = options.get('delay', 1.0)
        
        count_success = 0
        count_failed = 0
        count_no_referee = 0
        
        for i, match in enumerate(matches_without_referee):
            try:
                if not match.fixture_id:
                    self.stdout.write(self.style.WARNING(f"  Match has no fixture_id, skipping"))
                    count_failed += 1
                    continue
                
                # Make API call to get match details
                api_url = f"https://v3.football.api-sports.io/fixtures?id={match.fixture_id}"
                headers = {'x-apisports-key': settings.API_KEY}
                
                response = requests.get(api_url, headers=headers)
                
                if response.status_code != 200:
                    self.stdout.write(self.style.ERROR(f"  API call failed with status {response.status_code}"))
                    count_failed += 1
                    continue
                
                data = response.json()
                
                if not data.get('response'):
                    self.stdout.write(self.style.WARNING(f"  No data returned for fixture {match.fixture_id}"))
                    count_failed += 1
                    continue
                
                fixture_data = data['response'][0]['fixture']
                referee_name = fixture_data.get('referee')
                
                if not referee_name:
                    self.stdout.write(self.style.WARNING(f"  No referee name found for fixture {match.fixture_id}"))
                    count_no_referee += 1
                    continue
                
                # Get or create referee
                referee_user = sync_referee_to_database(referee_name)
                
                # Assign referee to match
                match.match_referee = referee_user
                match.save()
                
                self.stdout.write(self.style.SUCCESS(f"  Assigned referee {referee_user.username} to match {match}"))
                count_success += 1
                
                # Add delay to avoid hitting API rate limits
                if i < len(matches_without_referee) - 1 and delay > 0:
                    time.sleep(delay)
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  Error processing match {match}: {str(e)}"))
                count_failed += 1
        
        # Print summary
        self.stdout.write("\nReferee Reassignment Summary:")
        self.stdout.write(f"  Total matches processed: {len(matches_without_referee)}")
        self.stdout.write(self.style.SUCCESS(f"  Successfully assigned referees: {count_success}"))
        self.stdout.write(self.style.WARNING(f"  Matches with no referee data: {count_no_referee}"))
        self.stdout.write(self.style.ERROR(f"  Failed to process: {count_failed}"))