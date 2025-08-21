from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

class UserProfile(models.Model):
    USER_TYPES = (
        ('student', 'Student'),
        ('faculty', 'Faculty'),
        ('admin', 'Administrator'),
        ('staff', 'Staff'),
    )
    
    DEPARTMENTS = (
        ('computer_science', 'Computer Science'),
        ('engineering', 'Engineering'),
        ('business', 'Business Administration'),
        ('humanities', 'Humanities'),
        ('sciences', 'Sciences'),
        ('medicine', 'Medicine'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_type = models.CharField(max_length=20, choices=USER_TYPES, default='student')
    student_id = models.CharField(max_length=20, unique=True, null=True, blank=True)
    employee_id = models.CharField(max_length=20, unique=True, null=True, blank=True)
    department = models.CharField(max_length=50, choices=DEPARTMENTS, null=True, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    enrollment_year = models.IntegerField(null=True, blank=True)
    graduation_year = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.get_full_name()} ({self.get_user_type_display()})"
    
    def get_absolute_url(self):
        return reverse('accounts:profile')
    
    @property
    def full_name(self):
        return self.user.get_full_name() or self.user.username
    
    @property
    def is_student(self):
        return self.user_type == 'student'
    
    @property
    def is_faculty(self):
        return self.user_type == 'faculty'
    
    @property
    def is_admin(self):
        return self.user_type == 'admin'
