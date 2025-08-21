from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid

class Timetable(models.Model):
    DAYS_OF_WEEK = (
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday'),
    )
    
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='timetables')
    course = models.ForeignKey('lms.Course', on_delete=models.CASCADE)
    day_of_week = models.CharField(max_length=10, choices=DAYS_OF_WEEK)
    start_time = models.TimeField()
    end_time = models.TimeField()
    room = models.CharField(max_length=50)
    building = models.CharField(max_length=100)
    semester = models.CharField(max_length=20)
    academic_year = models.CharField(max_length=10)
    
    def __str__(self):
        return f"{self.course.code} - {self.get_day_of_week_display()} {self.start_time}"

class DigitalID(models.Model):
    student = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='digital_id',
        verbose_name="Student"
    )
    id_number = models.CharField(
        max_length=20,
        unique=True,
        default=uuid.uuid4,  # auto-generate if not provided
        editable=False
    )
    qr_code = models.ImageField(
        upload_to='qr_codes/',
        blank=True,
        null=True,
        verbose_name="QR Code"
    )
    is_active = models.BooleanField(default=True)
    issued_date = models.DateTimeField(auto_now_add=True)
    expiry_date = models.DateField()

    class Meta:
        verbose_name = "Digital ID"
        verbose_name_plural = "Digital IDs"
        ordering = ['-issued_date']

    def __str__(self):
        return f"Digital ID - {self.student.get_username()}"

    @property
    def is_expired(self):
        """Check if the Digital ID is expired."""
        return timezone.now().date() > self.expiry_date

    def deactivate_if_expired(self):
        """Automatically deactivate ID when expired."""
        if self.is_expired and self.is_active:
            self.is_active = False
            self.save(update_fields=['is_active'])



class AcademicRecord(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='academic_records')
    course = models.ForeignKey('lms.Course', on_delete=models.CASCADE)
    semester = models.CharField(max_length=20)
    academic_year = models.CharField(max_length=10)
    grade = models.CharField(max_length=2)
    grade_points = models.DecimalField(max_digits=3, decimal_places=2)
    credits_earned = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('student', 'course', 'semester', 'academic_year')
    
    def __str__(self):
        return f"{self.student.username} - {self.course.code} - {self.grade}"

class Event(models.Model):
    EVENT_TYPES = (
        ('academic', 'Academic'),
        ('cultural', 'Cultural'),
        ('sports', 'Sports'),
        ('workshop', 'Workshop'),
        ('seminar', 'Seminar'),
        ('exam', 'Examination'),
        ('holiday', 'Holiday'),
        ('maintenance', 'Maintenance'),
    )
    
    PRIORITY_LEVELS = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    )
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    priority = models.CharField(max_length=10, choices=PRIORITY_LEVELS, default='medium')
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    location = models.CharField(max_length=200)
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organized_events')
    target_audience = models.ManyToManyField(User, blank=True, related_name='targeted_events')
    is_public = models.BooleanField(default=True)
    max_attendees = models.IntegerField(null=True, blank=True)
    registration_required = models.BooleanField(default=False)
    registration_deadline = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.title} - {self.start_datetime.strftime('%Y-%m-%d')}"
    
    @property
    def is_upcoming(self):
        return self.start_datetime > timezone.now()
    
    @property
    def is_ongoing(self):
        now = timezone.now()
        return self.start_datetime <= now <= self.end_datetime

class EventRegistration(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='registrations')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='event_registrations')
    registered_at = models.DateTimeField(auto_now_add=True)
    attended = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ('event', 'student')
    
    def __str__(self):
        return f"{self.student.username} - {self.event.title}"

class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('academic', 'Academic'),
        ('event', 'Event'),
        ('system', 'System'),
        ('announcement', 'Announcement'),
        ('assignment', 'Assignment'),
        ('grade', 'Grade'),
    )
    
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.recipient.username} - {self.title}"

class LibraryResource(models.Model):
    RESOURCE_TYPES = (
        ('book', 'Book'),
        ('journal', 'Journal'),
        ('thesis', 'Thesis'),
        ('digital', 'Digital Resource'),
        ('multimedia', 'Multimedia'),
    )
    
    title = models.CharField(max_length=300)
    author = models.CharField(max_length=200)
    isbn = models.CharField(max_length=20, blank=True)
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPES)
    description = models.TextField(blank=True)
    publication_year = models.IntegerField()
    publisher = models.CharField(max_length=200, blank=True)
    total_copies = models.IntegerField(default=1)
    available_copies = models.IntegerField(default=1)
    location = models.CharField(max_length=100)
    digital_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.title} by {self.author}"
    
    @property
    def is_available(self):
        return self.available_copies > 0

class LibraryLoan(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='library_loans')
    resource = models.ForeignKey(LibraryResource, on_delete=models.CASCADE, related_name='loans')
    borrowed_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField()
    returned_date = models.DateTimeField(null=True, blank=True)
    is_returned = models.BooleanField(default=False)
    fine_amount = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    
    def __str__(self):
        return f"{self.student.username} - {self.resource.title}"
    
    @property
    def is_overdue(self):
        if self.is_returned:
            return False
        return timezone.now().date() > self.due_date
