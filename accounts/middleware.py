from django.shortcuts import redirect
from django.contrib import messages
from django.utils import timezone

class BanMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        if request.user.is_authenticated:
            # Auto-unban if ban period has expired
            if request.user.is_banned and request.user.ban_until:
                if timezone.now() > request.user.ban_until:
                    request.user.is_banned = False
                    request.user.ban_until = None
                    request.user.save()
            
            # Check if user is banned
            if request.user.is_banned:
                # Allow access to logout view
                if request.path.startswith('/logout/') or request.path.startswith('/accounts/logout/'):
                    response = self.get_response(request)
                    return response
                
                # Redirect to banned page for all other URLs
                if not request.path.startswith('/banned/'):
                    messages.error(request, "Your account has been temporarily banned.")
                    return redirect('accounts:banned')
        
        response = self.get_response(request)
        return response