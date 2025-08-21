from django.contrib import admin
from .models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'user_type', 'student_id', 'employee_id', 'department', 'created_at']
    list_filter = ['user_type', 'department', 'created_at']
    search_fields = ['user__username', 'user__email', 'student_id', 'employee_id']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'user_type')
        }),
        ('Identification', {
            'fields': ('student_id', 'employee_id', 'department')
        }),
        ('Personal Information', {
            'fields': ('phone_number', 'date_of_birth', 'address', 'profile_picture')
        }),
        ('Academic Information', {
            'fields': ('enrollment_year', 'graduation_year')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
