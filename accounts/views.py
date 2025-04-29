from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm, RefereeRegistrationForm, CustomLoginForm, RefereeDetailsForm
from django.contrib.auth import logout
from accounts.models import Vote
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.conf import settings
from django.core.files.base import ContentFile
import base64
from .models import ChatMessage
from django.contrib import messages
from django.views.generic import ListView, DetailView
from .models import PremierLeagueReferee
from datetime import datetime
import requests
import logging
from .models import CustomUser, Match, RefereePerformanceRating
from .forms import ExRefereeRegistrationForm, RefereeRatingForm 
import json
from django.http import JsonResponse
from django.db.models import Avg, Count
from django.db.models import Value
from django.db.models.functions import Concat
import random
import string
from django.views.decorators.csrf import csrf_protect
from django.db.models import Count, Case, When, IntegerField



def register_ex_referee(request):
    if request.method == "POST":
        form = ExRefereeRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.user_type = "ex_referee"  # Set user type to ex-referee
            user.is_current_referee = False  # Mark as an ex-referee
            user.save()
            login(request, user)  # Log in the new user
            messages.success(request, "Registration successful! Welcome to the system.")
            return redirect('accounts:home')  # Redirect to the ex-referee dashboard
    else:
        form = ExRefereeRegistrationForm()
    
    return render(request, "accounts/register_ex_referee.html", {"form": form})

def ex_referee_login(request):
    if request.user.is_authenticated and request.user.user_type == 'ex_referee':
        return redirect('accounts:ex_referee_dashboard')  # Redirect if already logged in

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None and user.user_type == 'ex_referee':
            login(request, user)
            return redirect('accounts:ex_referee_dashboard')  # Redirect after login
        else:
            messages.error(request, "Invalid credentials or unauthorized access.")

    return render(request, 'authentication/ex_referee_login.html')

@login_required
def ex_referee_dashboard(request):
    if request.user.user_type != 'ex_referee':
        messages.error(request, "You need to be logged in as an ex-referee to access this page.")
        return redirect('accounts:home')
    
    # Get all matches that have a referee assigned and are finished
    matches = Match.objects.filter(
        match_referee__isnull=False,
        status='FINISHED'
    ).order_by('-match_date')
    
    # Check which matches this ex-referee has already rated
    for match in matches:
        try:
            rating = RefereePerformanceRating.objects.get(
                match=match,
                ex_referee=request.user
            )
            match.user_rating = rating.rating_score
            match.has_rated = True
            match.feedback = rating.feedback

        except RefereePerformanceRating.DoesNotExist:
            match.has_rated = False
    
    context = {
        'matches': matches
    }
    return render(request, 'accounts/ex_referee_dashboard.html', context)

@login_required
@csrf_protect
def rate_referee(request, fixture_id):
    # Verify that the user is an ex-referee
    if request.user.user_type != 'ex_referee':
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'error': "You need to be logged in as an ex-referee to rate referees."}, status=403)
        messages.error(request, "You need to be logged in as an ex-referee to rate referees.")
        return redirect('home')
    
    match = get_object_or_404(Match, fixture_id=fixture_id)
    
    # Check if match has a referee assigned
    if match.match_referee is None:
        # Try to find and assign the referee from the API data
        try:
            # First, try to get the referee name from your existing match data
            referee_name = None
            
            # If you store the referee name in a custom field on the Match model
            if hasattr(match, 'referee_name') and match.referee_name:
                referee_name = match.referee_name
            
            # If you don't have the referee name stored, fetch it from the API
            if not referee_name:
                # Use your existing API connection code
                api_url = f"https://v3.football.api-sports.io/fixtures?id={match.fixture_id}"
                api_key = settings.API_KEY
                headers = {
                    'x-apisports-key': api_key
                }
                
                response = requests.get(api_url, headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    # Extract referee name from API response
                    fixture_data = data.get('response', [{}])[0].get('fixture', {})
                    referee_name = fixture_data.get('referee')
                else:
                    raise Exception(f"API returned status {response.status_code}")
            
            # If we found a referee name, find or create the referee user
            if referee_name:
                # Use the same logic from your sync function to find the referee
                referee_user = sync_referee_to_database(referee_name)
                # Assign the referee to this match
                match.match_referee = referee_user
                match.save()
            else:
                raise Exception("No referee name found for this match")
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'error': f"Could not find referee for this match: {str(e)}"}, status=404)
            messages.error(request, f"Could not find referee for this match: {str(e)}")
            return redirect('home')
    
    # If we still don't have a referee, return an error
    if match.match_referee is None:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'error': "This match has no referee assigned."}, status=404)
        messages.error(request, "This match has no referee assigned.")
        return redirect('home')
    
    # Check if the referee has already been rated by this ex-referee
    try:
        rating = RefereePerformanceRating.objects.get(match=match, ex_referee=request.user)
    except RefereePerformanceRating.DoesNotExist:
        rating = None
    
    if request.method == 'POST':
        # Check if this is an AJAX request expecting JSON
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        # For AJAX/JSON requests
        if is_ajax:
            try:
                data = json.loads(request.body)
                rating_value = data.get('rating')

                if rating_value is None:
                    return JsonResponse({'error': 'Rating value is required'}, status=400)
                
                if rating is None:
                    rating = RefereePerformanceRating(match=match, ex_referee=request.user)
                
                rating.rating_score = rating_value
                
                # Optional: Add feedback if provided
                feedback = data.get('feedback')
                if feedback:
                    rating.feedback = feedback
                
                rating.save()
                
                # Get referee full name or username
                referee = match.match_referee
                referee_display_name = referee.get_full_name() if referee.get_full_name() else referee.username
                
                # Get average rating for this referee
                avg_rating = RefereePerformanceRating.objects.filter(
                    match__match_referee=referee
                ).aggregate(Avg('rating_score'))['rating_score__avg']
                
                return JsonResponse({
                    'success': True,
                    'message': f"Your rating for {referee_display_name} has been submitted.",
                    'rating': float(rating.rating_score),  # Convert Decimal to float for JSON
                    'referee_id': referee.id,
                    'referee_name': referee_display_name,
                    'average_rating': float(avg_rating) if avg_rating else None
                })
            except json.JSONDecodeError:
                return JsonResponse({'error': 'Invalid JSON data'}, status=400)
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=500)
        
        # For regular form submissions (non-AJAX)
        else:
            form = RefereeRatingForm(request.POST, instance=rating)
            if form.is_valid():
                rating = form.save(commit=False)
                rating.match = match
                rating.ex_referee = request.user
                rating.save()
                messages.success(request, f"Your rating for {match.match_referee.username} has been submitted.")
                return redirect('accounts:ex_referee_dashboard')
    else:
        form = RefereeRatingForm(instance=rating)
    
    context = {
        'form': form,
        'match': match
    }
    return render(request, 'accounts/rate_referee.html', context)

from django.shortcuts import render
from django.db.models import Avg, Count, Max, Min
from django.template.loader import render_to_string
from django.http import JsonResponse

def get_referee_ratings_summary(request):
    """Ajax view to get referee ratings summary data as JSON"""
    # Get all users who are referees
    referees = CustomUser.objects.filter(user_type='referee')
    
    # For each referee, calculate their average rating and other stats
    referee_stats = []
    for referee in referees:
        # Get matches where this referee officiated and received ratings
        matches_with_ratings = referee.matches_officiated.filter(referee_ratings__isnull=False).distinct()
        
        # If they have no rated matches, include with null values
        if not matches_with_ratings.exists():
            referee_stats.append({
                'referee_id': referee.id,
                'referee_name': referee.get_full_name() or referee.username,
                'avg_rating': None,
                'total_matches_rated': 0,
                'total_ratings': 0,
                'highest_rating': None,
                'lowest_rating': None
            })
            continue
        
        # Get all ratings for this referee across all matches
        ratings = RefereePerformanceRating.objects.filter(match__match_referee=referee)
        
        # Calculate stats
        stats = ratings.aggregate(
            avg_rating=Avg('rating_score'),
            total_ratings=Count('id'),
            highest_rating=Max('rating_score'),
            lowest_rating=Min('rating_score')
        )
        
        referee_stats.append({
            'referee_id': referee.id,
            'referee_name': referee.get_full_name() or referee.username,
            'avg_rating': float(stats['avg_rating']) if stats['avg_rating'] else None,
            'total_matches_rated': matches_with_ratings.count(),
            'total_ratings': stats['total_ratings'],
            'highest_rating': float(stats['highest_rating']) if stats['highest_rating'] else None,
            'lowest_rating': float(stats['lowest_rating']) if stats['lowest_rating'] else None
        })
    
    # Sort by average rating (highest first)
    referee_stats = sorted(
        referee_stats, 
        key=lambda x: x['avg_rating'] if x['avg_rating'] is not None else 0, 
        reverse=True
    )

    # Debug: Print what we're returning
    print("Returning JSON data:", referee_stats)

    
    return JsonResponse({'referees': referee_stats}, content_type='application/json')

@login_required
def referee_feedback(request):
    """
    View for referees to see feedback on their performances
    """
    # Check if user is a referee
    if request.user.user_type != 'referee':
        messages.error(request, "Only referees can access this page.")
        return redirect('accounts:home')  # or any other appropriate page
    
    # Get all ratings for this referee
    ratings = RefereePerformanceRating.objects.filter(
        match__match_referee=request.user
    ).select_related('match').order_by('-match__match_date')
    
    # Calculate average rating if ratings exist
    average_rating = None
    if ratings.exists():
        total_rating = sum(rating.rating_score for rating in ratings)
        average_rating = total_rating / ratings.count()
    
    context = {
        'ratings': ratings,
        'average_rating': average_rating
    }
    
    return render(request, 'accounts/referee_feedback.html', context)

def most_recent_match_rating(request):
    """Get ratings and details for the most recent match"""
    # Find the most recent match that has ratings
    most_recent_match = Match.objects.filter(
        referee_ratings__isnull=False
    ).order_by('-match_date').first()
    
    if not most_recent_match:
        return JsonResponse({
            'success': False,
            'message': 'No rated matches found'
        })
    
    # Get the referee for this match
    referee = most_recent_match.match_referee
    
    # Get all ratings for this match
    match_ratings = RefereePerformanceRating.objects.filter(match=most_recent_match)

    # Calculate average rating for this match
    avg_rating = match_ratings.aggregate(Avg('rating_score'))['rating_score__avg']
    
    # Get detailed match information
    match_data = {
        'match_id': most_recent_match.fixture_id,
        'home_team': {
            'name': most_recent_match.home_team.name,
            'logo': most_recent_match.home_team.logo.url if most_recent_match.home_team.logo else None,
            'score': most_recent_match.home_score,
            'yellow_cards': most_recent_match.yellow_cards_home,
            'red_cards': most_recent_match.red_cards_home
        },
        'away_team': {
            'name': most_recent_match.away_team.name,
            'logo': most_recent_match.away_team.logo.url if most_recent_match.away_team.logo else None,
            'score': most_recent_match.away_score,
            'yellow_cards': most_recent_match.yellow_cards_away,
            'red_cards': most_recent_match.red_cards_away
        },
        'date': most_recent_match.match_date.strftime('%d %b %Y - %H:%M'),
        'venue': most_recent_match.venue,
        'status': most_recent_match.status,
        'referee': {
            'name': referee.get_full_name() if referee else 'Unknown',
            'avg_rating': float(avg_rating) if avg_rating else None,
            'total_ratings': match_ratings.count()
        },
        'stats': {
            'yellow_cards_total': most_recent_match.yellow_cards_home + most_recent_match.yellow_cards_away,
            'red_cards_total': most_recent_match.red_cards_home + most_recent_match.red_cards_away,
            'penalties_given': most_recent_match.penalties_given
        }
    }
    
    return JsonResponse({
        'success': True,
        'match': match_data
    })


@login_required
def my_referee_ratings(request):
    """View for ex-referees to see all ratings they've given"""
    if request.user.user_type != 'ex_referee':
        messages.error(request, "You need to be logged in as an ex-referee to view your ratings.")
        return redirect('home')
    
    # Get all ratings submitted by this ex-referee
    ratings = RefereePerformanceRating.objects.filter(ex_referee=request.user).select_related(
        'match', 'match__match_referee', 'match__home_team', 'match__away_team'
    ).order_by('-created_at')
    
    context = {
        'ratings': ratings
    }
    
    # If it's an AJAX request, return just the ratings HTML
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        html = render_to_string('accounts/my_ratings_table.html', context)
        return JsonResponse({'html': html})
    
    # Otherwise return the full page (though we'll use AJAX in this case)
    return render(request, 'accounts/my_ratings.html', context)

def fetch_and_sync_referees_from_api():
    """
    Fetch referee data from the API and sync it to the database
    """
    # API configuration - replace with your actual API details
    api_url = "https://v3.football.api-sports.io//fixtures"  # For example: "https://api-football-v1.p.rapidapi.com/v3/fixtures"
    

    api_key = settings.API_KEY
    # Your API headers - typically includes authentication
    headers = {
        'x-apisports-key': api_key
    }
    
    # Parameters to fetch matches (adjust according to your API)
    params = {
        'league': '39',  # Premier League ID (for example)
        'season': '2024'  # Current season
    }
    
    try:
        response = requests.get(api_url, headers=headers, params=params)
        response.raise_for_status()  # Raise exception for HTTP errors
        
        data = response.json()
        
        # Process each match to extract referees
        referees_synced = []
        
        # Assuming your API returns a list of fixtures in a 'response' key
        for fixture in data.get('response', []):
            # Extract referee name from the fixture data
            # Adjust this based on the actual structure of your API response
            referee_name = fixture.get('fixture', {}).get('referee')
            
            if referee_name and referee_name not in referees_synced:
                # Sync the referee to the database
                referee_user = sync_referee_to_database(referee_name)
                referees_synced.append(referee_name)
                
        return f"Successfully synced {len(referees_synced)} referees from the API"
        
    except requests.exceptions.RequestException as e:
        return f"Error fetching data from API: {str(e)}"

def sync_referee_to_database(api_referee_name):
    print(f"DEBUG: Original API referee name: {api_referee_name}")
    """
    Sync a referee from the API to the database
    Returns the referee user object
    """
    print(f"Processing referee: {api_referee_name}")  # Debug line
    
    # Remove country if present (format is usually "Name, Country")
    if "," in api_referee_name:
        api_referee_name = api_referee_name.split(",", 1)[0].strip()
    
    # Now split the name into parts
    name_parts = api_referee_name.split()
    
    # Try to match by last name first (more reliable)
    if len(name_parts) >= 1:
        last_name = name_parts[-1]
        
        # Get all referees with this last name
        existing_referees = CustomUser.objects.filter(
            user_type='referee',
            last_name__iexact=last_name
        )
        
        # If we have multiple with the same last name, try to narrow it down
        if existing_referees.exists():
            # If full name, try to match first name too
            if len(name_parts) >= 2:
                first_name = ' '.join(name_parts[:-1])
                for ref in existing_referees:
                    if ref.first_name.lower() == first_name.lower():
                        print(f"Found existing referee: {ref.username} for {api_referee_name}")
                        return ref
            
            # If we couldn't narrow it down but have only one match, return that
            if existing_referees.count() == 1:
                print(f"Found single matching referee: {existing_referees.first().username} for {api_referee_name}")
                return existing_referees.first()
    
    # If we get here, we need to create a new referee
    print(f"No existing referee found for '{api_referee_name}', creating new one")
    
    if len(name_parts) >= 2:
        # Get first initial and last name
        first_initial = name_parts[0][0].lower()
        last_name = name_parts[-1].lower()
        base_username = f"{first_initial}{last_name}"
    else:   
        # Fallback if we only have one name part
        base_username = name_parts[0].lower()
    
    # Initialize username with base_username
    username = base_username
    
    # Ensure username is unique
    counter = 1
    while CustomUser.objects.filter(username=username).exists():
        username = f"{base_username}{counter}"
        counter += 1
    
    # Create the new referee user
    new_referee = CustomUser(
        username=username,
        user_type='referee',
        is_approved=True,  # Auto-approve API referees
    )
    
    # Set the name fields based on the format
    if len(name_parts) >= 2:
        new_referee.first_name = ' '.join(name_parts[:-1])
        new_referee.last_name = name_parts[-1]
    else:
        # Single word name
        new_referee.last_name = name_parts[0]
    
    # Set a random password
    random_password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
    new_referee.set_password(random_password)
    
    new_referee.save()
    print(f"Created new referee: {new_referee.username} ({api_referee_name})")
    return new_referee


@login_required
def my_latest_performance(request):
    """Get the latest match for the currently logged-in referee"""
    print(f"my_latest_performance view called by user: {request.user.username}")
    
    if request.user.user_type != 'referee':
        return JsonResponse({
            "success": False,
            "message": 'Only referee accounts can access this information'
        })
    
    # Finds the most recent match officiated by this referee, regardless of ratings
    most_recent_match = Match.objects.filter(
        match_referee=request.user
    ).order_by('-match_date').first()
    
    if not most_recent_match:
        return JsonResponse({
            'success': False,
            'message': 'No matches found for you',
            'career': {
                'total_matches': 0,
                'rated_matches': 0
            }
        })
    
    # Gets all ratings for this match
    match_ratings = RefereePerformanceRating.objects.filter(match=most_recent_match)
    
    # Calculate average rating for this match
    avg_rating = match_ratings.aggregate(Avg('rating_score'))['rating_score__avg']
    
    # Use getattr to safely get attributes that might not exist yet with default values
    yellow_cards_home = getattr(most_recent_match, 'yellow_cards_home', 0)
    yellow_cards_away = getattr(most_recent_match, 'yellow_cards_away', 0)
    red_cards_home = getattr(most_recent_match, 'red_cards_home', 0)
    red_cards_away = getattr(most_recent_match, 'red_cards_away', 0)
    penalties_given = getattr(most_recent_match, 'penalties_given', 0)
    
    # Gets detailed match information
    match_data = {
        'match_id': most_recent_match.fixture_id,
        'home_team': {
            'name': most_recent_match.home_team.name,
            'logo': most_recent_match.home_team.logo.url if most_recent_match.home_team.logo else None,
            'score': most_recent_match.home_score,
            'yellow_cards': yellow_cards_home,
            'red_cards': red_cards_home
        },
        'away_team': {
            'name': most_recent_match.away_team.name,
            'logo': most_recent_match.away_team.logo.url if most_recent_match.away_team.logo else None,
            'score': most_recent_match.away_score,
            'yellow_cards': yellow_cards_away,
            'red_cards': red_cards_away
        },
        'date': most_recent_match.match_date.strftime('%d %b %Y - %H:%M'),
        'venue': most_recent_match.venue,
        'status': most_recent_match.status,
        'ratings': {
            'avg_rating': float(avg_rating) if avg_rating else None,
            'total_ratings': match_ratings.count(),
            'highest': match_ratings.aggregate(Max('rating_score'))['rating_score__max'],
            'lowest': match_ratings.aggregate(Min('rating_score'))['rating_score__min']
        },
        'stats': {
            'yellow_cards_total': yellow_cards_home + yellow_cards_away,
            'red_cards_total': red_cards_home + red_cards_away,
            'penalties_given': penalties_given
        }
    }
    return JsonResponse({
        'success': True,
        'match': match_data,
    })

def update_match_stats(match):
    """Update statistics (cards, penalties) for a match from the API"""
    if not match.fixture_id:
        print(f"Match {match} has no fixture_id, skipping")
        return False
    
    # Skip if no referee is assigned
    if not match.match_referee:
        print(f"Match {match} has no referee assigned, skipping")
        return False
    
    api_key = settings.API_KEY
    headers = {"x-apisports-key": api_key}
    
    # Get events for this match
    events_url = f"https://v3.football.api-sports.io/fixtures/events?fixture={match.fixture_id}"
    
    try:
        response = requests.get(events_url, headers=headers)
        
        if response.status_code != 200:
            print(f"API call failed with status {response.status_code}")
            return False
        
        data = response.json()
        events = data.get('response', [])
        
        if not events:
            print(f"No events found for match {match}")
            return False
        
        yellow_home = 0
        yellow_away = 0
        red_home = 0
        red_away = 0
        penalties = 0
        
        # Process all referee-issued cards and penalties
        for event in events:
            # Extract team information
            team_id = event.get('team', {}).get('id')
            is_home_team = team_id == match.home_team.external_id
            
            # Check for yellow cards
            if event.get('type') == 'Card' and event.get('detail') == 'Yellow Card':
                if is_home_team:
                    yellow_home += 1
                else:
                    yellow_away += 1
            
            # Check for red cards
            if event.get('type') == 'Card' and (event.get('detail') == 'Red Card' or event.get('detail') == 'Second Yellow card'):
                if is_home_team:
                    red_home += 1
                else:
                    red_away += 1
            
            # Check for penalties
            if event.get('type') == 'Goal' and event.get('detail') == 'Penalty':
                penalties += 1
            elif event.get('type') == 'Var' and 'penalty' in event.get('detail', '').lower():
                penalties += 1
        
        # Update match with card counts
        match.yellow_cards_home = yellow_home
        match.yellow_cards_away = yellow_away
        match.red_cards_home = red_home
        match.red_cards_away = red_away
        match.penalties_given = penalties
        match.save()
        
        # Print the referee who issued these cards
        referee_name = match.match_referee.get_full_name() or match.match_referee.username
        print(f"Referee {referee_name} issued: YH:{yellow_home}, YA:{yellow_away}, RH:{red_home}, RA:{red_away}, P:{penalties} in match {match}")
        
        return True
        
    except Exception as e:
        print(f"Error updating match {match}: {str(e)}")
        return False
    
def referee_season_leaderboard(request):
    """
    Display a leaderboard of referee performance metrics for the current season
    """
    # Define current season date range with timezone awareness
    from django.utils import timezone
    from datetime import datetime
    from django.db.models import Avg, Count, Sum, F, FloatField, ExpressionWrapper
    import random  # For generating random poor decision values
    
    season_start = datetime(2024, 8, 1, tzinfo=timezone.get_current_timezone())
    season_end = datetime(2025, 5, 31, tzinfo=timezone.get_current_timezone())
    
    # Get all referees who have officiated matches this season
    referees = CustomUser.objects.filter(
        user_type='referee',
        matches_officiated__match_date__gte=season_start,
        matches_officiated__match_date__lte=season_end
    ).distinct()
    
    leaderboard = []
    
    for referee in referees:
        # Get all matches officiated by this referee this season
        matches = Match.objects.filter(
            match_referee=referee,
            match_date__gte=season_start,
            match_date__lte=season_end
        )
        
        total_matches = matches.count()
        
        if total_matches == 0:
            continue  # Skip referees with no matches
        
        # Get average rating
        ratings = RefereePerformanceRating.objects.filter(
            match__in=matches
        )
        
        avg_rating = ratings.aggregate(avg=Avg('rating_score'))['avg']
        total_ratings = ratings.count()
        
        # Card statistics
        yellow_cards = matches.aggregate(
            total=Sum(F('yellow_cards_home') + F('yellow_cards_away'))
        )['total'] or 0
        
        red_cards = matches.aggregate(
            total=Sum(F('red_cards_home') + F('red_cards_away'))
        )['total'] or 0
        
        penalties = matches.aggregate(total=Sum('penalties_given'))['total'] or 0
        
        # Calculate per-match averages
        yellow_per_match = float(yellow_cards) / total_matches if total_matches > 0 else 0
        red_per_match = float(red_cards) / total_matches if total_matches > 0 else 0
        penalties_per_match = float(penalties) / total_matches if total_matches > 0 else 0
        
        # Generate random poor decisions per game (between 0.5 and 3.0)
        # We'll use a normal distribution centered around quality - higher rated referees have fewer poor decisions
        base_poor_decisions = random.uniform(0.5, 3.0)
        rating_factor = float(avg_rating or 5.0) / 10.0  # Convert rating to a 0-1 scale
        poor_decisions_per_match = round(base_poor_decisions * (1.5 - rating_factor), 1)  # Inverse relationship with rating

        total_poor_decisions = int(poor_decisions_per_match * total_matches)

        
        print(f"Referee: {referee.username}, Poor decisions: {total_poor_decisions}, Per match: {poor_decisions_per_match}")

        leaderboard.append({
            'referee': referee,
            'name': referee.get_full_name() or referee.username,
            'matches': total_matches,
            'avg_rating': avg_rating,
            'total_ratings': total_ratings,
            'yellow_cards': yellow_cards,
            'red_cards': red_cards,
            'penalties': penalties,
            'yellow_per_match': yellow_per_match,
            'red_per_match': red_per_match,
            'penalties_per_match': penalties_per_match,
            'poor_decisions': total_poor_decisions,
            'poor_decisions_per_match': poor_decisions_per_match
        })
    
    # Sort the leaderboard by average rating (highest first)
    leaderboard = sorted(
        leaderboard,
        key=lambda x: (x['avg_rating'] or 0),  # Use 0 if avg_rating is None
        reverse=True
    )
    
    return render(request, 'accounts/referee_leaderboard.html', {
        'leaderboard': leaderboard,
        'season': '2024-2025'
    })

    
def home(request):
    print("====== HOME VIEW CALLED ======")
    video_url = "https://www.youtube.com/watch?v=dUep4EpJT9Q"
    

    # API configuration
    api_key = settings.API_KEY
    headers = {"x-apisports-key": api_key}
    
    # Current Premier League season
    current_season = 2024
    league_id = 39  # Premier League ID
    
    # Initialize variables for template context
    live_matches = []
    past_matches = []
    upcoming_matches = []
    previous_gameweek_matches = []
    standings = []
    current_round = None
    previous_round = None
    
    try:
        print(f"API Key being used: {api_key[:5]}...")  # Security-conscious logging
        
        # Get current date in ISO format for filtering
        from datetime import datetime, timedelta
        today = datetime.now().strftime("%Y-%m-%d")
        ten_days_ago = (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d")
        ten_days_ahead = (datetime.now() + timedelta(days=10)).strftime("%Y-%m-%d")
        
        # 1. Fetch live matches
        live_url = f"https://v3.football.api-sports.io/fixtures?live=all&league={league_id}"
        live_response = requests.get(live_url, headers=headers)
        if live_response.status_code == 200:
            live_matches = live_response.json().get('response', [])
            print(f"Found {len(live_matches)} live Premier League matches")
        
        # 2. Fetch recent completed matches (last 10 days)
        recent_url = f"https://v3.football.api-sports.io/fixtures?league={league_id}&season={current_season}&from={ten_days_ago}&to={today}&status=FT"
        recent_response = requests.get(recent_url, headers=headers)
        if recent_response.status_code == 200:
            past_matches = recent_response.json().get('response', [])
            print(f"Found {len(past_matches)} recent finished matches")
            
            # Sort by date (most recent first)
            past_matches = sorted(
                past_matches, 
                key=lambda x: x.get('fixture', {}).get('date', ''), 
                reverse=True
            )
        
        # 3. Fetch upcoming matches (next 10 days)
        upcoming_url = f"https://v3.football.api-sports.io/fixtures?league={league_id}&season={current_season}&from={today}&to={ten_days_ahead}"
        upcoming_response = requests.get(upcoming_url, headers=headers)
        if upcoming_response.status_code == 200:
            upcoming_matches = upcoming_response.json().get('response', [])
            print(f"Found {len(upcoming_matches)} upcoming matches")
            
            # Sort by date (soonest first)
            upcoming_matches = sorted(
                upcoming_matches, 
                key=lambda x: x.get('fixture', {}).get('date', '')
            )
        
        
        rounds_url = f"https://v3.football.api-sports.io/fixtures/rounds?current=true&league={league_id}&season={current_season}"
        rounds_response = requests.get(rounds_url, headers=headers)
        if rounds_response.status_code == 200:
            rounds_data = rounds_response.json().get('response', [])
            if rounds_data:
                current_round = rounds_data[0]
                print(f"Current round: {current_round}")
                
                # Try to determine previous round
                all_rounds_url = f"https://v3.football.api-sports.io/fixtures/rounds?league={league_id}&season={current_season}"
                all_rounds_response = requests.get(all_rounds_url, headers=headers)
                
                if all_rounds_response.status_code == 200:
                    all_rounds = all_rounds_response.json().get('response', [])
                    
                    # Get previous round
                    current_round_parts = current_round.split(' - ')
                    if len(current_round_parts) == 2 and current_round_parts[1].isdigit():
                        current_round_num = int(current_round_parts[1])
                        previous_round_num = current_round_num - 1
                        previous_round = f"{current_round_parts[0]} - {previous_round_num}"
                        
                        # Fetch fixtures for the previous round
                        if previous_round in all_rounds:
                            previous_fixtures_url = f"https://v3.football.api-sports.io/fixtures?league={league_id}&season={current_season}&round={previous_round}"
                            previous_fixtures_response = requests.get(previous_fixtures_url, headers=headers)
                            
                            if previous_fixtures_response.status_code == 200:
                                previous_gameweek_matches = previous_fixtures_response.json().get('response', [])
                                print(f"Found {len(previous_gameweek_matches)} fixtures for the previous gameweek")
                                
                                # Sort by date
                                previous_gameweek_matches = sorted(
                                    previous_gameweek_matches, 
                                    key=lambda x: x.get('fixture', {}).get('date', ''), 
                                    reverse=True
                                )
        
        # 5. Fetch standings
        standings_url = f"https://v3.football.api-sports.io/standings?league={league_id}&season={current_season}"
        standings_response = requests.get(standings_url, headers=headers)
        if standings_response.status_code == 200:
            standings_data = standings_response.json().get('response', [])
            if standings_data:
                standings = standings_data[0].get('league', {}).get('standings', [[]])[0]
        
        # If we don't have any past_matches but we have previous_gameweek_matches, use those
        if not past_matches and previous_gameweek_matches:
            past_matches = previous_gameweek_matches
        
        # Render template with all collected data
        return render(request, 'accounts/home.html', {
            "video_url": video_url,
            "live_matches": live_matches,
            "past_matches": past_matches,  # Recent completed matches
            "upcoming_matches": upcoming_matches,  # Added upcoming matches
            "previous_gameweek_matches": previous_gameweek_matches,
            "standings": standings,
            "current_round": current_round,
            "previous_round": previous_round
        })
        
    except Exception as e:
        print(f"API Error: {str(e)}")
        # Render without API data on error
        return render(request, 'accounts/home.html', {"video_url": video_url})

def logout_view(request):
    logout(request)
    return redirect('accounts:home')

def get_league_standings(request):
    """
    API endpoint to get Premier League standings data
    """
    api_key = settings.API_KEY
    headers = {"x-apisports-key": api_key}
    
    # Current Premier League season
    current_season = 2024
    league_id = 39  # Premier League ID
    
    # Standings URL
    standings_url = f"https://v3.football.api-sports.io/standings?league={league_id}&season={current_season}"
    
    try:
        standings_response = requests.get(standings_url, headers=headers)
        
        if standings_response.status_code == 200:
            standings_data = standings_response.json().get('response', [])
            if standings_data:
                standings = standings_data[0].get('league', {}).get('standings', [[]])[0]
                return JsonResponse({
                    'success': True,
                    'standings': standings,
                    'timestamp': datetime.now().isoformat()
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'No standings data available'
                })
        else:
            return JsonResponse({
                'success': False,
                'error': f"API request failed with status code: {standings_response.status_code}"
            })
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })
        
def register_referee(request):
    # Initialize the form variable outside the conditional blocks
    form = None

    if request.method == "POST":
        if 'step1' in request.POST:  # First step: Basic registration
            form = RefereeRegistrationForm(request.POST)
            if form.is_valid():
                user = form.save(commit=False)
                user.is_approved = False  # Set account as unapproved by default
                user.registration_complete = False  # Registration not yet complete
                user.save()
                login(request, user)  # Log the user in after step 1
                return redirect('accounts:register_referee_step2')  # Redirect to step 2
        elif 'step2' in request.POST:  # Second step: Additional details
            form = RefereeDetailsForm(request.POST, instance=request.user)
            if form.is_valid():
                user = form.save(commit=False)
                user.registration_complete = True  # Mark registration as complete
                user.save()
                messages.success(request, "Your registration is complete and pending admin approval.")
                return redirect('accounts:pending_approval')  # Redirect to pending approval page
    else:
        if request.user.is_authenticated and request.user.user_type == 'referee':
            if not request.user.registration_complete:  # Redirect to step 2 if not completed
                form = RefereeDetailsForm(instance=request.user)
                return render(request, 'accounts/register_referee_step2.html', {'form': form})
            else:
                return redirect('accounts:pending_approval')  # Redirect to pending approval if already completed
        else:
            form = RefereeRegistrationForm()  # Show step 1 form for new referees

    # Ensure the form is always defined before rendering
    if form is None:
        form = RefereeRegistrationForm()  # Fallback to the step 1 form

    return render(request, 'accounts/register_referee.html', {'form': form})


def pending_approval(request):
    return render(request, 'accounts/pending_approval.html')

def register_user (request):
    print(f"Template path: {request.path}")

    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.save()
            login(request, user)
            return redirect('accounts:home')  # Redirect to home page after registration
    else:
        form = UserRegistrationForm()
    return render(request, 'accounts/register_user.html', {'form': form})

def user_login(request):
    print(f"Template path: {request.path}")

    if request.method == "POST":
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.user_type == 'referee' and not user.is_approved:
                    messages.error(request, "Your account is pending admin approval.")
                    return redirect('accounts:login')
                login(request, user)
                return redirect('accounts:home')
    else:
        form = CustomLoginForm()
    return render(request, 'accounts/login.html', {'form': form})

@login_required
def fan_chat(request):
    messages = ChatMessage.objects.select_related('user').order_by('-timestamp')[:50]

    return render(request, 'accounts/fan_chat.html', {'messages': messages})

@login_required
def send_message(request):
    if request.method == 'POST':
        content = request.POST.get('content')
        audio_data = request.POST.get('audio')
        
        message = ChatMessage(user=request.user)
        
        if content:
            message.content = content
        elif audio_data:
            # Handle audio data (base64 encoded)
            audio_file = ContentFile(base64.b64decode(audio_data.split(',')[1]))
            message.audio_message.save('audio_message.wav', audio_file)
        
        message.save()
        
        return JsonResponse({
            'status': 'success',
            'message': {
                'id': message.id,
                'user': message.user.username,
                'content': message.content,
                'audio_url': message.audio_message.url if message.audio_message else None,
                'timestamp': message.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            }
        })
    
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def get_messages(request):
    messages = ChatMessage.objects.select_related('user').order_by('-timestamp')[:50]
    return JsonResponse({
        'messages': [{
            'id': msg.id,
            'user': msg.user.username,
            'content': msg.content,
            'audio_url': msg.audio_message.url if msg.audio_message else None,
            'timestamp': msg.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        } for msg in messages]
    })


def logout_view(request):
    logout(request)
    return redirect('accounts:home')


def submit_vote(request):
    if request.method == "POST":
        user = request.user
        choice = request.POST.get("choice")
        match_id = request.POST.get("match_id")

        if not user.is_authenticated:
            return JsonResponse({"error": "You must be logged in to vote"}, status=403)

        # Check if user already voted, update vote instead
        vote, created = Vote.objects.update_or_create(user=user, match_id=match_id, defaults={"choice": choice})

        # Calculate new percentages
        total_votes = Vote.objects.filter(match_id=match_id).count()
        yes_votes = Vote.objects.filter(match_id=match_id, choice="yes").count()
        no_votes = Vote.objects.filter(match_id = match_id, choice="no").count()

        yes_percentage = round((yes_votes / total_votes) * 100, 2) if total_votes > 0 else 0
        no_percentage = round((no_votes / total_votes) * 100, 2) if total_votes > 0 else 0
        
        response_data = {"yes": yes_percentage, "no": no_percentage}
        print(f"Sending response for match {match_id}: {response_data}")
        return JsonResponse(response_data)

        #return JsonResponse({"yes": yes_percentage, "no": no_percentage})

def get_vote_results(request, match_id):
    """API endpoint to get the vote results for a specific match"""
    # Count total votes for this match
    vote_count = Vote.objects.filter(match_id=match_id).count()
    
    if vote_count == 0:
        # If no votes, return default values
        return JsonResponse({
            'yes': 0,
            'no': 0,
            'total_votes': 0
        })
    
    # Get the vote breakdown
    vote_data = Vote.objects.filter(match_id=match_id).aggregate(
        yes_count=Count(Case(When(choice='yes', then=1), output_field=IntegerField())),
        no_count=Count(Case(When(choice='no', then=1), output_field=IntegerField()))
    )
    
    # Calculate percentages
    yes_count = vote_data['yes_count']
    no_count = vote_data['no_count']
    
    yes_percentage = round((yes_count / vote_count) * 100)
    no_percentage = round((no_count / vote_count) * 100)
    
    # Return JSON response
    return JsonResponse({
        'yes': yes_percentage,
        'no': no_percentage,
        'total_votes': vote_count
    })

def banned_view(request):
    ban_reason = request.user.ban_reason
    ban_until = request.user.ban_until
    return render(request, 'accounts/banned.html', {
        'ban_reason': ban_reason,
        'ban_until': ban_until
    })

from django.shortcuts import render
from django.conf import settings
import requests
from django.http import JsonResponse


@login_required
def referee_profile(request):
    context = {
        'user': request.user,
        'referee': request.user
    }
    return render(request, 'accounts/profile.html', context)

@login_required
def upload_profile_picture(request):
    from .forms import ProfilePictureForm  

    if request.method == 'POST':
        form = ProfilePictureForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            user = form.save(commit=False)
            user.profile_picture_approved = False  # Resets approval status
            user.save()
            return redirect('accounts:referee_profile')  # Redirect back to profile page
    else:
        form = ProfilePictureForm(instance=request.user)

    return render(request, 'accounts/upload_picture.html', {'form': form})



def referee_stats_dashboard(request):
    referees = PremierLeagueReferee.objects.all().order_by('poor_decisions', '-performance_rating')
    context = {
        'referees': referees,
        'current_season': "2024/25"
    }
    return render(request, 'accounts/home.html', context)


logger = logging.getLogger(__name__)

def match_details_api(request, match_id):
    api_url = f"https://v3.football.api-sports.io/fixtures"
    params = {"id": match_id}
    headers = {"x-apisports-key": settings.API_KEY}

    logger.info(f"Fetching match details for ID: {match_id}")
    
    try:
        response = requests.get(api_url, params=params, headers=headers)
        logger.info(f"API Response Status: {response.status_code}")

        data = response.json()
        logger.info(f"Full API Response: {data}")  # Logs entire response

        if 'response' in data and isinstance(data['response'], list) and data['response']:
            logger.info("Returning match data")
            return JsonResponse(data['response'][0])  # Sends the first match object

        logger.warning(f"No match data found for ID: {match_id}")
        return JsonResponse({"error": "Match not found"}, status=404)

    except requests.exceptions.RequestException as e:
        logger.error(f"Request Error: {e}")
        return JsonResponse({"error": "Request failed"}, status=500)