from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from administration.models import Department


class Course(models.Model):
    COURSE_LEVELS = (
        ('undergraduate', 'Undergraduate'),
        ('postgraduate', 'Postgraduate'),
        ('diploma', 'Diploma'),
        ('certificate', 'Certificate'),
    )
    
    title = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField()
    level = models.CharField(max_length=20, choices=COURSE_LEVELS)
    credits = models.IntegerField()
    instructor = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='taught_courses'
    )
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name="courses") 
    prerequisites = models.ManyToManyField(
        'self', blank=True, symmetrical=False
    )
    max_students = models.IntegerField(default=50)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at'] 
    
    def __str__(self):
        return f"{self.code} - {self.title}"
    
    def get_absolute_url(self):
        return reverse('lms:course_detail', kwargs={'pk': self.pk})
    
    # ✅ renamed to avoid clash with ORM annotations
    @property
    def enrolled_students_count(self):
        """
        Returns the number of active enrollments for this course.
        """
        return self.enrollments.filter(is_active=True).count()
    
    # (Optional) easy check if the course is full
    @property
    def is_full(self):
        return self.enrolled_students_count >= self.max_students



class Enrollment(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    final_grade = models.CharField(max_length=2, blank=True)
    
    class Meta:
        unique_together = ('student', 'course')
    
    def __str__(self):
        return f"{self.student.username} - {self.course.code}"

class Module(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=200)
    description = models.TextField()
    order = models.PositiveIntegerField()
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.course.code} - {self.title}"

class Lesson(models.Model):
    LESSON_TYPES = (
        ('video', 'Video'),
        ('document', 'Document'),
        ('presentation', 'Presentation'),
        ('quiz', 'Quiz'),
        ('assignment', 'Assignment'),
    )
    
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    content = models.TextField(blank=True)
    lesson_type = models.CharField(max_length=20, choices=LESSON_TYPES)
    file_upload = models.FileField(upload_to='lessons/', blank=True, null=True)
    video_url = models.URLField(blank=True)
    order = models.PositiveIntegerField()
    duration_minutes = models.IntegerField(default=0)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.module.course.code} - {self.title}"

class Assignment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='assignments')
    title = models.CharField(max_length=200)
    description = models.TextField()
    instructions = models.TextField()
    due_date = models.DateTimeField()
    max_points = models.IntegerField(default=100)
    file_upload = models.FileField(upload_to='assignments/', blank=True, null=True)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.course.code} - {self.title}"
    
    @property
    def is_overdue(self):
        return timezone.now() > self.due_date

class Submission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submissions')
    content = models.TextField(blank=True)
    file_upload = models.FileField(upload_to='submissions/', blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    grade = models.IntegerField(null=True, blank=True)
    feedback = models.TextField(blank=True)
    graded_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ('assignment', 'student')
    
    def __str__(self):
        return f"{self.student.username} - {self.assignment.title}"
    
    @property
    def is_late(self):
        return self.submitted_at > self.assignment.due_date

class Quiz(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='quizzes')
    title = models.CharField(max_length=200)
    description = models.TextField()
    time_limit_minutes = models.IntegerField(default=60)
    max_attempts = models.IntegerField(default=1)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.course.code} - {self.title}"

class Question(models.Model):
    QUESTION_TYPES = (
        ('multiple_choice', 'Multiple Choice'),
        ('true_false', 'True/False'),
        ('short_answer', 'Short Answer'),
        ('essay', 'Essay'),
    )
    
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    points = models.IntegerField(default=1)
    order = models.PositiveIntegerField()
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"Q{self.order}: {self.question_text[:50]}..."

class QuizAttempt(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='attempts')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_attempts')
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    score = models.IntegerField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.student.username} - {self.quiz.title} (Attempt)"
