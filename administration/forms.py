from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Department, Room, MaintenanceRequest, Announcement, SystemReport
from accounts.models import UserProfile
from lms.models import Course
import csv
from io import TextIOWrapper

class UserEditForm(forms.ModelForm):
    """Form for editing user information by admin"""
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'is_active', 'is_staff']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-uct-blue focus:ring-uct-blue sm:text-sm'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-uct-blue focus:ring-uct-blue sm:text-sm'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-uct-blue focus:ring-uct-blue sm:text-sm'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-uct-blue focus:ring-uct-blue sm:text-sm'
            }),
        }


class UserProfileEditForm(forms.ModelForm):
    """Form for editing user profile by admin"""
    
    class Meta:
        model = UserProfile
        fields = ['user_type', 'student_id', 'employee_id', 'department', 'phone_number', 'date_of_birth']
        widgets = {
            'user_type': forms.Select(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-uct-blue focus:ring-uct-blue sm:text-sm'
            }),
            'student_id': forms.TextInput(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-uct-blue focus:ring-uct-blue sm:text-sm'
            }),
            'employee_id': forms.TextInput(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-uct-blue focus:ring-uct-blue sm:text-sm'
            }),
            'department': forms.Select(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-uct-blue focus:ring-uct-blue sm:text-sm'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-uct-blue focus:ring-uct-blue sm:text-sm'
            }),
            'date_of_birth': forms.DateInput(attrs={
                'type': 'date',
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-uct-blue focus:ring-uct-blue sm:text-sm'
            }),
        }


class DepartmentForm(forms.ModelForm):
    """Form for creating/editing departments"""
    
    class Meta:
        model = Department
        fields = ['name', 'code', 'description', 'head_of_department', 'building', 'phone', 'email']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-uct-blue focus:ring-uct-blue sm:text-sm'
            }),
            'code': forms.TextInput(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-uct-blue focus:ring-uct-blue sm:text-sm'
            }),
            'description': forms.Textarea(attrs={
                'rows': 3,
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-uct-blue focus:ring-uct-blue sm:text-sm'
            }),
            'head_of_department': forms.Select(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-uct-blue focus:ring-uct-blue sm:text-sm'
            }),
            'building': forms.TextInput(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-uct-blue focus:ring-uct-blue sm:text-sm'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-uct-blue focus:ring-uct-blue sm:text-sm'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-uct-blue focus:ring-uct-blue sm:text-sm'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter head to only faculty/staff
        self.fields['head_of_department'].queryset = User.objects.filter(
            userprofile__user_type__in=['faculty', 'admin']
        )


class RoomForm(forms.ModelForm):
    """Form for creating/editing rooms"""
    
    class Meta:
        model = Room
        fields = ['number', 'building', 'room_type', 'capacity', 'has_projector', 'has_whiteboard', 'has_computer', 'has_internet', 'is_accessible', 'description']
        widgets = {
            'number': forms.TextInput(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-uct-blue focus:ring-uct-blue sm:text-sm'
            }),
            'building': forms.TextInput(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-uct-blue focus:ring-uct-blue sm:text-sm'
            }),
            'room_type': forms.Select(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-uct-blue focus:ring-uct-blue sm:text-sm'
            }),
            'capacity': forms.NumberInput(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-uct-blue focus:ring-uct-blue sm:text-sm'
            }),
            'description': forms.Textarea(attrs={
                'rows': 3,
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-uct-blue focus:ring-uct-blue sm:text-sm'
            }),
        }


class MaintenanceRequestForm(forms.ModelForm):
    """Form for creating/updating maintenance requests"""
    
    class Meta:
        model = MaintenanceRequest
        fields = ['title', 'description', 'priority', 'location', 'status', 'assigned_to']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-uct-blue focus:ring-uct-blue sm:text-sm'
            }),
            'description': forms.Textarea(attrs={
                'rows': 4,
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-uct-blue focus:ring-uct-blue sm:text-sm'
            }),
            'priority': forms.Select(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-uct-blue focus:ring-uct-blue sm:text-sm'
            }),
            'location': forms.TextInput(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-uct-blue focus:ring-uct-blue sm:text-sm'
            }),
            'status': forms.Select(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-uct-blue focus:ring-uct-blue sm:text-sm'
            }),
            'assigned_to': forms.Select(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-uct-blue focus:ring-uct-blue sm:text-sm'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter assigned_to to only staff/admin
        self.fields['assigned_to'].queryset = User.objects.filter(
            userprofile__user_type__in=['admin', 'faculty']
        )


class AnnouncementForm(forms.ModelForm):
    """Form for creating/editing announcements"""
    
    class Meta:
        model = Announcement
        fields = ['title', 'content', 'announcement_type', 'is_urgent', 'is_published', 'publish_date', 'expiry_date']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-uct-blue focus:ring-uct-blue sm:text-sm'
            }),
            'content': forms.Textarea(attrs={
                'rows': 6,
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-uct-blue focus:ring-uct-blue sm:text-sm'
            }),
            'announcement_type': forms.Select(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-uct-blue focus:ring-uct-blue sm:text-sm'
            }),
            'publish_date': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-uct-blue focus:ring-uct-blue sm:text-sm'
            }),
            'expiry_date': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-uct-blue focus:ring-uct-blue sm:text-sm'
            }),
        }


class SystemReportForm(forms.ModelForm):
    """Form for generating system reports"""
    
    class Meta:
        model = SystemReport
        fields = ['title', 'description', 'report_type', 'is_public']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-uct-blue focus:ring-uct-blue sm:text-sm'
            }),
            'description': forms.Textarea(attrs={
                'rows': 3,
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-uct-blue focus:ring-uct-blue sm:text-sm'
            }),
            'report_type': forms.Select(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-uct-blue focus:ring-uct-blue sm:text-sm'
            }),
            'is_public': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 text-uct-blue focus:ring-uct-blue border-gray-300 rounded'
            }),
        }


class BulkUserUploadForm(forms.Form):
    """Form for bulk user upload via CSV"""
    
    csv_file = forms.FileField(
        widget=forms.FileInput(attrs={
            'class': 'block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-uct-blue file:text-white hover:file:bg-blue-700',
            'accept': '.csv'
        }),
        help_text="Upload a CSV file with columns: username, first_name, last_name, email, user_type"
    )
    
    def clean_csv_file(self):
        csv_file = self.cleaned_data['csv_file']
        
        if not csv_file.name.endswith('.csv'):
            raise ValidationError('File must be a CSV file.')
        
        if csv_file.size > 5 * 1024 * 1024:  # 5MB limit
            raise ValidationError('File size must be less than 5MB.')
        
        return csv_file
    
    def process_csv(self):
        """Process the CSV file and return users to create"""
        csv_file = self.cleaned_data['csv_file']
        users_to_create = []
        errors = []
        
        try:
            file_data = TextIOWrapper(csv_file.file, encoding='utf-8')
            csv_reader = csv.DictReader(file_data)
            
            required_headers = ['username', 'first_name', 'last_name', 'email', 'user_type']
            if not all(header in csv_reader.fieldnames for header in required_headers):
                raise ValidationError(f"CSV must contain columns: {', '.join(required_headers)}")
            
            row_number = 1
            for row in csv_reader:
                row_number += 1
                
                try:
                    username = row['username'].strip()
                    
                    # Check if user already exists
                    if User.objects.filter(username=username).exists():
                        errors.append(f"Row {row_number}: Username '{username}' already exists")
                        continue
                    
                    # Validate email
                    email = row['email'].strip()
                    if User.objects.filter(email=email).exists():
                        errors.append(f"Row {row_number}: Email '{email}' already exists")
                        continue
                    
                    # Validate user type
                    user_type = row['user_type'].strip().lower()
                    if user_type not in ['student', 'faculty', 'admin']:
                        errors.append(f"Row {row_number}: Invalid user type '{user_type}'")
                        continue
                    
                    user_data = {
                        'username': username,
                        'first_name': row['first_name'].strip(),
                        'last_name': row['last_name'].strip(),
                        'email': email,
                        'user_type': user_type
                    }
                    
                    users_to_create.append(user_data)
                    
                except Exception as e:
                    errors.append(f"Row {row_number}: {str(e)}")
            
        except Exception as e:
            raise ValidationError(f"Error processing CSV file: {str(e)}")
        
        if errors:
            raise ValidationError("CSV processing errors:\n" + "\n".join(errors))
        
        return users_to_create
