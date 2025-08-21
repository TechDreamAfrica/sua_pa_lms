from django import forms
from django.contrib.auth.models import User
from .models import UserProfile

class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-uct-blue focus:ring-uct-blue sm:text-sm',
                'placeholder': 'Enter your first name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-uct-blue focus:ring-uct-blue sm:text-sm',
                'placeholder': 'Enter your last name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-uct-blue focus:ring-uct-blue sm:text-sm',
                'placeholder': 'Enter your email address'
            }),
        }

class UserProfileEditForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['phone_number', 'date_of_birth', 'address', 'department', 
                  'profile_picture', 'enrollment_year', 'graduation_year']
        widgets = {
            'phone_number': forms.TextInput(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-uct-blue focus:ring-uct-blue sm:text-sm',
                'placeholder': 'Enter your phone number'
            }),
            'date_of_birth': forms.DateInput(attrs={
                'type': 'date',
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-uct-blue focus:ring-uct-blue sm:text-sm'
            }),
            'address': forms.Textarea(attrs={
                'rows': 3,
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-uct-blue focus:ring-uct-blue sm:text-sm',
                'placeholder': 'Enter your full address'
            }),
            'department': forms.Select(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-uct-blue focus:ring-uct-blue sm:text-sm'
            }),
            'profile_picture': forms.FileInput(attrs={
                'class': 'block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-uct-blue file:text-white hover:file:bg-blue-700',
                'accept': 'image/*'
            }),
            'enrollment_year': forms.NumberInput(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-uct-blue focus:ring-uct-blue sm:text-sm',
                'min': '1950',
                'max': '2030'
            }),
            'graduation_year': forms.NumberInput(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-uct-blue focus:ring-uct-blue sm:text-sm',
                'min': '1950',
                'max': '2030'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make certain fields optional based on user type
        if self.instance and self.instance.user_type != 'student':
            self.fields['enrollment_year'].required = False
            self.fields['graduation_year'].required = False
