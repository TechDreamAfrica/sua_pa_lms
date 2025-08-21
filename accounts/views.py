from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.views.generic import TemplateView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.views import View
from .models import UserProfile
from .forms import UserEditForm, UserProfileEditForm

class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    
    def get_success_url(self):
        if hasattr(self.request.user, 'userprofile'):
            if self.request.user.userprofile.is_admin:
                return reverse_lazy('administration:dashboard')
            elif self.request.user.userprofile.is_faculty:
                return reverse_lazy('lms:dashboard')
            else:
                return reverse_lazy('lms:dashboard')
        return reverse_lazy('lms:dashboard')

class CustomLogoutView(View):
    """Custom logout view that handles both GET and POST requests"""
    
    def get(self, request):
        """Handle GET request by showing logout confirmation"""
        if not request.user.is_authenticated:
            messages.info(request, 'You are already logged out.')
            return redirect('accounts:login')
        return render(request, 'accounts/logout_confirm.html')
    
    def post(self, request):
        """Handle POST request to actually log out the user"""
        if request.user.is_authenticated:
            username = request.user.username
            logout(request)
            messages.success(request, f'Goodbye {username}! You have been successfully logged out.')
        else:
            messages.info(request, 'You were already logged out.')
        return redirect('accounts:login')

class LogoutConfirmView(LoginRequiredMixin, TemplateView):
    """Simple logout confirmation view"""
    template_name = 'accounts/logout_confirm.html'

class RegisterView(CreateView):
    form_class = UserCreationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:login')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        # Create user profile
        UserProfile.objects.create(user=self.object)
        messages.success(self.request, 'Registration successful! Please log in.')
        return response

class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/profile.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        context['profile'] = profile
        return context

class ProfileEditView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/profile_edit.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        
        context['user_form'] = UserEditForm(instance=self.request.user)
        context['profile_form'] = UserProfileEditForm(instance=profile)
        context['profile'] = profile
        return context
    
    def post(self, request, *args, **kwargs):
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        
        user_form = UserEditForm(request.POST, instance=request.user)
        profile_form = UserProfileEditForm(request.POST, request.FILES, instance=profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile')
        else:
            context = self.get_context_data(**kwargs)
            context['user_form'] = user_form
            context['profile_form'] = profile_form
            return self.render_to_response(context)
