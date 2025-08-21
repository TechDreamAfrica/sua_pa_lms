from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)
    description = models.TextField(blank=True)
    head_of_department = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='headed_departments')
    building = models.CharField(max_length=100)
    phone = models.CharField(max_length=15, blank=True)
    email = models.EmailField(blank=True)
    budget = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.code} - {self.name}"

class Faculty(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    dean = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='dean_faculties')
    departments = models.ManyToManyField(Department, related_name='faculties')
    established_year = models.IntegerField()
    
    class Meta:
        verbose_name_plural = "Faculties"
    
    def __str__(self):
        return self.name

class Semester(models.Model):
    SEMESTER_TYPES = (
        ('fall', 'Fall'),
        ('spring', 'Spring'),
        ('summer', 'Summer'),
        ('winter', 'Winter'),
    )
    
    name = models.CharField(max_length=20, choices=SEMESTER_TYPES)
    academic_year = models.CharField(max_length=10)  # e.g., "2023-2024"
    start_date = models.DateField()
    end_date = models.DateField()
    registration_start = models.DateField()
    registration_end = models.DateField()
    is_current = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ('name', 'academic_year')
    
    def __str__(self):
        return f"{self.get_name_display()} {self.academic_year}"

class Room(models.Model):
    ROOM_TYPES = (
        ('classroom', 'Classroom'),
        ('laboratory', 'Laboratory'),
        ('lecture_hall', 'Lecture Hall'),
        ('seminar_room', 'Seminar Room'),
        ('computer_lab', 'Computer Lab'),
        ('library', 'Library'),
        ('office', 'Office'),
        ('conference_room', 'Conference Room'),
    )
    
    number = models.CharField(max_length=20)
    building = models.CharField(max_length=100)
    room_type = models.CharField(max_length=20, choices=ROOM_TYPES)
    capacity = models.IntegerField()
    has_projector = models.BooleanField(default=False)
    has_whiteboard = models.BooleanField(default=True)
    has_computer = models.BooleanField(default=False)
    has_internet = models.BooleanField(default=True)
    is_accessible = models.BooleanField(default=True)
    description = models.TextField(blank=True)
    
    class Meta:
        unique_together = ('number', 'building')
    
    def __str__(self):
        return f"{self.building} - {self.number}"

class RoomBooking(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='bookings')
    booked_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='room_bookings')
    purpose = models.CharField(max_length=200)
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    is_approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_bookings')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.room} - {self.start_datetime.strftime('%Y-%m-%d %H:%M')}"
    
    @property
    def is_upcoming(self):
        return self.start_datetime > timezone.now()

class AttendanceRecord(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attendance_records')
    course = models.ForeignKey('lms.Course', on_delete=models.CASCADE, related_name='attendance_records')
    date = models.DateField()
    is_present = models.BooleanField(default=False)
    marked_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='marked_attendance')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('student', 'course', 'date')
    
    def __str__(self):
        status = "Present" if self.is_present else "Absent"
        return f"{self.student.username} - {self.course.code} - {self.date} ({status})"

class SystemReport(models.Model):
    REPORT_TYPES = (
        ('enrollment', 'Enrollment Report'),
        ('attendance', 'Attendance Report'),
        ('performance', 'Performance Report'),
        ('resource_usage', 'Resource Usage Report'),
        ('financial', 'Financial Report'),
        ('user_activity', 'User Activity Report'),
    )
    
    title = models.CharField(max_length=200)
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    description = models.TextField()
    generated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='generated_reports')
    generated_at = models.DateTimeField(auto_now_add=True)
    file_path = models.FileField(upload_to='reports/', null=True, blank=True)
    is_public = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.title} - {self.generated_at.strftime('%Y-%m-%d')}"

class MaintenanceRequest(models.Model):
    PRIORITY_LEVELS = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=200)
    priority = models.CharField(max_length=10, choices=PRIORITY_LEVELS, default='medium')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    requested_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='maintenance_requests')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_maintenance')
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    estimated_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    actual_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    def __str__(self):
        return f"{self.title} - {self.get_status_display()}"

class Announcement(models.Model):
    ANNOUNCEMENT_TYPES = (
        ('general', 'General'),
        ('academic', 'Academic'),
        ('administrative', 'Administrative'),
        ('emergency', 'Emergency'),
        ('event', 'Event'),
    )
    
    title = models.CharField(max_length=200)
    content = models.TextField()
    announcement_type = models.CharField(max_length=20, choices=ANNOUNCEMENT_TYPES, default='general')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='announcements')
    target_groups = models.ManyToManyField('auth.Group', blank=True)
    is_urgent = models.BooleanField(default=False)
    is_published = models.BooleanField(default=False)
    publish_date = models.DateTimeField(null=True, blank=True)
    expiry_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.title
    
    @property
    def is_active(self):
        now = timezone.now()
        if self.expiry_date:
            return self.is_published and now <= self.expiry_date
        return self.is_published
