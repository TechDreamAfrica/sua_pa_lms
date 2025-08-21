from django.contrib import admin
from .models import Course, Enrollment, Module, Lesson, Assignment, Submission, Quiz, Question, QuizAttempt

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['code', 'title', 'instructor', 'level', 'credits', 'is_active', 'created_at']
    list_filter = ['level', 'department', 'is_active', 'created_at']
    search_fields = ['title', 'code', 'instructor__username']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'enrolled_at', 'is_active', 'final_grade']
    list_filter = ['is_active', 'enrolled_at', 'course__level']
    search_fields = ['student__username', 'course__title', 'course__code']

@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ['course', 'title', 'order', 'is_published', 'created_at']
    list_filter = ['is_published', 'created_at']
    search_fields = ['title', 'course__title']

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['module', 'title', 'lesson_type', 'order', 'is_published', 'duration_minutes']
    list_filter = ['lesson_type', 'is_published', 'created_at']
    search_fields = ['title', 'module__title']

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ['course', 'title', 'due_date', 'max_points', 'is_published', 'created_at']
    list_filter = ['is_published', 'due_date', 'created_at']
    search_fields = ['title', 'course__title', 'course__code']

@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ['assignment', 'student', 'submitted_at', 'grade', 'is_late']
    list_filter = ['submitted_at', 'graded_at']
    search_fields = ['student__username', 'assignment__title']
    readonly_fields = ['submitted_at', 'is_late']

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ['course', 'title', 'time_limit_minutes', 'max_attempts', 'is_published', 'created_at']
    list_filter = ['is_published', 'created_at']
    search_fields = ['title', 'course__title']

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['quiz', 'question_text', 'question_type', 'points', 'order']
    list_filter = ['question_type', 'quiz__course']
    search_fields = ['question_text', 'quiz__title']

@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ['quiz', 'student', 'started_at', 'completed_at', 'score']
    list_filter = ['started_at', 'completed_at']
    search_fields = ['student__username', 'quiz__title']
