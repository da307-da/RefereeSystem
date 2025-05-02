from django.core.management.base import BaseCommand
from django.conf import settings
import requests
from accounts.models import Match, Team
import json
from datetime import datetime

class Command(BaseCommand):
    help = 'Import matches from api-sports'
    
    def handle(self, *args, **options):
        try:
            # Get your API key from settings
            api_key = settings.API_KEY
            
            # API endpoint for matches
            url = "https://v3.football.api-sports.io/fixtures"
            
            # Test API connection first
            self.stdout.write(self.style.SUCCESS(f'Testing API connection...'))
            test_response = requests.get(url, headers={"x-apisports-key": api_key}, params={"league": 39, "season": 2024})
            
            if test_response.status_code == 200:
                test_data = test_response.json()
                self.stdout.write(f"API connection successful")
                
                if 'errors' in test_data and test_data['errors']:
                    self.stdout.write(self.style.ERROR(f"API reported errors: {test_data['errors']}"))
                    return
            else:
                self.stdout.write(self.style.ERROR(f"API connection failed: {test_response.status_code}"))
                return
            
            # Processes matches for the current season
            for season in [2024]:
                self.stdout.write(self.style.SUCCESS(f'\nImporting Premier League matches for season {season}...'))
                
                params = {
                    "league": 39,  # Premier League
                    "season": season,
                    "status": "FT"
                }
                
                headers = {
                    "x-apisports-key": api_key
                }
                
                response = requests.get(url, headers=headers, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if 'errors' in data and data['errors']:
                        self.stdout.write(self.style.ERROR(f"API reported errors: {data['errors']}"))
                        continue
                    
                    fixtures = data.get('response', [])
                    self.stdout.write(f"Found {len(fixtures)} fixtures for season {season}")
                    
                    # Processes each fixture
                    for fixture in fixtures:
                        fixture_data = fixture.get('fixture', {})
                        teams_data = fixture.get('teams', {})
                        goals_data = fixture.get('goals', {})
                        
                        # Extracts the API fixture ID
                        api_fixture_id = fixture_data.get('id')
                        
                        if api_fixture_id is None:
                            self.stdout.write(self.style.WARNING(f"Skipping fixture without ID"))
                            continue
                        
                        # Checks if match already exists in our database
                        existing_match = Match.objects.filter(fixture_id=api_fixture_id).first()
                        
                        if existing_match:
                            self.stdout.write(f"Updating existing match: {api_fixture_id}")
                            # Updates existing match with latest data
                            self._update_match(existing_match, fixture_data, teams_data, goals_data)
                        else:
                            self.stdout.write(f"Creating new match: {api_fixture_id}")
                            # Creates new match
                            self._create_match(api_fixture_id, fixture_data, teams_data, goals_data)
                
                else:
                    self.stdout.write(self.style.ERROR(f"API request failed for season {season}: {response.status_code}"))
            
            self.stdout.write(self.style.SUCCESS('Match import completed successfully'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {str(e)}"))
    
    def _get_or_create_team(self, team_data):
        """Helper method to get or create a team"""
        team_name = team_data.get('name')
        team_id = team_data.get('id')
        
        if not team_name:
            raise ValueError("Team name is required")
        
        # Tries to find the team by external ID first
        team = Team.objects.filter(external_id=team_id).first()
        
        if not team:
            # Then tries by name
            team = Team.objects.filter(name=team_name).first()
        
        if not team:
            # Creates new team if it doesn't exist
            team = Team.objects.create(
                name=team_name,
                external_id=team_id,
                logo=team_data.get('logo', '')
            )
            self.stdout.write(f"Created new team: {team_name}")
        
        return team
    
    def _create_match(self, api_fixture_id, fixture_data, teams_data, goals_data):
        """Helper method to create a new match"""
        try:
            # Gets or creates teams
            home_team = self._get_or_create_team(teams_data.get('home', {}))
            away_team = self._get_or_create_team(teams_data.get('away', {}))
            
            # Parses match date
            match_date_str = fixture_data.get('date')
            match_date = datetime.fromisoformat(match_date_str.replace('Z', '+00:00')) if match_date_str else None
            
            # Determines match status
            api_status = fixture_data.get('status', {}).get('short')
            if api_status == 'FT':
                status = 'FINISHED'
            elif api_status in ['1H', '2H', 'HT']:
                status = 'LIVE'
            else:
                status = 'SCHEDULED'
            
            # Creates the match
            Match.objects.create(
                fixture_id=api_fixture_id,
                home_team=home_team,
                away_team=away_team,
                match_date=match_date,
                venue=fixture_data.get('venue', {}).get('name', 'Unknown'),
                home_score=goals_data.get('home'),
                away_score=goals_data.get('away'),
                status=status,
                # Referee will need to be assigned separately, as API data might not match your user model
            )
            
            self.stdout.write(self.style.SUCCESS(f"Created match: {home_team} vs {away_team}"))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error creating match {api_fixture_id}: {str(e)}"))
    
    def _update_match(self, match, fixture_data, teams_data, goals_data):
        """Helper method to update an existing match"""
        try:
            # Updates match details
            match_date_str = fixture_data.get('date')
            if match_date_str:
                match.match_date = datetime.fromisoformat(match_date_str.replace('Z', '+00:00'))
            
            match.venue = fixture_data.get('venue', {}).get('name', match.venue)
            
            # Updates scores if available
            home_score = goals_data.get('home')
            away_score = goals_data.get('away')
            if home_score is not None:
                match.home_score = home_score
            if away_score is not None:
                match.away_score = away_score
            
            # Updates status
            api_status = fixture_data.get('status', {}).get('short')
            if api_status == 'FT':
                match.status = 'FINISHED'
            elif api_status in ['1H', '2H', 'HT']:
                match.status = 'LIVE'
            
            # Saves the updated match
            match.save()
            
            self.stdout.write(f"Updated match: {match}")
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error updating match {match.fixture_id}: {str(e)}"))