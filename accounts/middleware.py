from django.contrib.auth import logout
from django.contrib import messages
from django.shortcuts import redirect
from django.utils import timezone
from datetime import timedelta

class SessionTimeoutMiddleware:
    """Middleware to handle session timeouts"""
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            # Check if session has expired (24 hours)
            if 'last_activity' in request.session:
                last_activity = request.session['last_activity']
                if timezone.now().timestamp() - last_activity > 24 * 60 * 60:  # 24 hours
                    logout(request)
                    messages.warning(request, 'Your session has expired. Please log in again.')
                    return redirect('accounts:login')
            
            # Update last activity
            request.session['last_activity'] = timezone.now().timestamp()
        
        response = self.get_response(request)
        return response
