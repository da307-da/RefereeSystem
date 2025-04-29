from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'accounts' 



urlpatterns = [


    path('', views.home, name='home'), 
    path('register/referee/', views.register_referee, name='register_referee'),
    path('register/referee/step2/', views.register_referee, name='register_referee_step2'),
    path('register/user/', views.register_user, name='register_user'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.logout_view, name='logout'),  # Logout page
    path('submit-vote/', views.submit_vote, name='submit_vote'),
    path('profile/', views.referee_profile, name='referee_profile'),
    path('fan-chat/', views.fan_chat, name='fan_chat'),
    path('upload-profile-picture/', views.upload_profile_picture, name='upload_profile_picture'),
    path('send-message/', views.send_message, name='send_message'),
    path('get-messages/', views.get_messages, name='get_messages'),
    path('pending_approval/', views.pending_approval, name='pending_approval'),
    path('dashboard/', views.referee_stats_dashboard, name='dashboard'),
    path('api/match/<int:match_id>/', views.match_details_api, name='match_details_api'),
    path('ex-referee/login/', views.ex_referee_login, name='ex_referee_login'),
    path("register/ex-referee/", views.register_ex_referee, name="register_ex_referee"),
    path('ex-referee/dashboard/', views.ex_referee_dashboard, name='ex_referee_dashboard'),
    path('rate-referee/<int:fixture_id>/', views.rate_referee, name='rate_referee'),
    path('accounts/get-referee-ratings-summary/', views.get_referee_ratings_summary, name='get_referee_ratings_summary'),
    path('most-recent-match-rating/', views.most_recent_match_rating, name='most_recent_match_rating'),
    path('my-latest-performance/', views.my_latest_performance, name='my_latest_performance'),
    path('referee-leaderboard/', views.referee_season_leaderboard, name='referee_leaderboard'),
    path('banned/', views.banned_view, name='banned'),
    path('referee/feedback/', views.referee_feedback, name='referee_feedback'),
    path('api/vote-results/<int:match_id>/', views.get_vote_results, name='get_vote_results')



]




# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)