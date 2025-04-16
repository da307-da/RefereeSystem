from django.core.management.base import BaseCommand
from accounts.models import Match
from django.conf import settings
import requests
from accounts.views import sync_referee_to_database
import time
from django.utils import timezone
from datetime import datetime
from zoneinfo import ZoneInfo 


class Command(BaseCommand):
    help = 'Assign referees to matches that don\'t have referees assigned'

    def add_arguments(self, parser):
        parser.add_argument('--limit', type=int, help='Limit number of matches to process')
        parser.add_argument('--delay', type=float, default=1.0, help='Delay between API calls (seconds)')

    def handle(self, *args, **options):
        # Define current season date range (approximate)
        season_start = timezone.make_aware(
            datetime(2024, 8, 1), 
            timezone=ZoneInfo('UTC'),       
        )    
        season_end = timezone.make_aware(
            datetime(2025, 5, 31), 
            timezone=ZoneInfo('UTC')
        )
        # Filter for matches within this season that have no referee assigned
        matches = Match.objects.filter(
            match_referee=None,
            match_date__gte=season_start,
            match_date__lte=season_end
        )
        total = matches.count()        
            
        self.stdout.write(f"Found {total} matches without referees assigned")
        
        limit = options.get('limit')
        if limit:
            matches = matches[:limit]
            self.stdout.write(f"Processing first {limit} matches")
        
        delay = options.get('delay')
        
        count_success = 0
        count_failed = 0
        count_no_referee = 0
        
        # Process each match
        for i, match in enumerate(matches):
            try:
                self.stdout.write(f"Processing match {i+1}/{len(matches)}: {match}")
                
                if not match.fixture_id:
                    self.stdout.write(self.style.WARNING(f"  Match has no fixture_id, skipping"))
                    count_failed += 1
                    continue
                
                # Make API call to get match details
                api_url = f"https://v3.football.api-sports.io/fixtures?id={match.fixture_id}"
                headers = {'x-apisports-key': settings.API_KEY}
                
                self.stdout.write(f"  Calling API for fixture {match.fixture_id}")
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
                if i < len(matches) - 1 and delay > 0:
                    time.sleep(delay)
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  Error processing match {match}: {str(e)}"))
                count_failed += 1
        
        # Print summary
        self.stdout.write("\nSummary:")
        self.stdout.write(f"  Total matches processed: {len(matches)}")
        self.stdout.write(self.style.SUCCESS(f"  Successfully assigned referees: {count_success}"))
        self.stdout.write(self.style.WARNING(f"  Matches with no referee data: {count_no_referee}"))
        self.stdout.write(self.style.ERROR(f"  Failed to process: {count_failed}"))