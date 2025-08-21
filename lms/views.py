from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, ListView, DetailView, CreateView
from django.contrib import messages
from django.db.models import Count, Q
from .models import Course, Enrollment, Assignment, Submission, Quiz, Module
from accounts.models import UserProfile
from django.db.models import Avg, Max

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'lms/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get user profile
        profile, created = UserProfile.objects.get_or_create(user=user)
        
        if profile.is_student:
            # Student dashboard data
            enrolled_courses = Course.objects.filter(
                enrollments__student=user,
                enrollments__is_active=True
            )
            pending_assignments = Assignment.objects.filter(
                course__in=enrolled_courses,
                is_published=True
            ).exclude(
                submissions__student=user
            )[:5]
            
            context.update({
                'enrolled_courses': enrolled_courses,
                'pending_assignments': pending_assignments,
                'total_courses': enrolled_courses.count(),
                'pending_assignments_count': pending_assignments.count(),
            })
        
        elif profile.is_faculty:
            # Faculty dashboard data
            taught_courses = Course.objects.filter(instructor=user)
            total_students = Enrollment.objects.filter(
                course__in=taught_courses,
                is_active=True
            ).count()
            
            context.update({
                'taught_courses': taught_courses,
                'total_students': total_students,
                'total_courses': taught_courses.count(),
            })
        
        return context

class CourseListView(LoginRequiredMixin, ListView):
    model = Course
    template_name = 'lms/course_list.html'
    context_object_name = 'courses'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Course.objects.filter(is_active=True)
        search = self.request.GET.get('search')
        department = self.request.GET.get('department')
        
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | 
                Q(code__icontains=search) |
                Q(description__icontains=search)
            )
        
        if department:
            queryset = queryset.filter(department=department)
            
        return queryset.annotate(
            enrolled_count=Count('enrollments', filter=Q(enrollments__is_active=True))
        )

class CourseDetailView(LoginRequiredMixin, DetailView):
    model = Course
    template_name = 'lms/course_detail.html'
    context_object_name = 'course'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.object
        user = self.request.user
        
        # Check if user is enrolled
        is_enrolled = Enrollment.objects.filter(
            student=user,
            course=course,
            is_active=True
        ).exists()
        
        context['is_enrolled'] = is_enrolled
        context['modules'] = course.modules.filter(is_published=True).order_by('order')
        context['assignments'] = course.assignments.filter(is_published=True)[:5]
        context['quizzes'] = course.quizzes.filter(is_published=True)[:5]
        
        return context

class EnrollCourseView(LoginRequiredMixin, TemplateView):
    def post(self, request, pk):
        course = get_object_or_404(Course, pk=pk, is_active=True)
        
        # Check if already enrolled
        enrollment, created = Enrollment.objects.get_or_create(
            student=request.user,
            course=course,
            defaults={'is_active': True}
        )
        
        if created:
            messages.success(request, f'Successfully enrolled in {course.title}!')
        else:
            if enrollment.is_active:
                messages.info(request, f'You are already enrolled in {course.title}.')
            else:
                enrollment.is_active = True
                enrollment.save()
                messages.success(request, f'Re-enrolled in {course.title}!')
        
        return redirect('lms:course_detail', pk=pk)

class ModuleDetailView(LoginRequiredMixin, DetailView):
    model = Module
    template_name = 'lms/module_detail.html'
    context_object_name = 'module'
    pk_url_kwarg = 'module_id'
    
    def get_object(self):
        course_id = self.kwargs.get('course_id')
        module_id = self.kwargs.get('module_id')
        return get_object_or_404(
            Module,
            pk=module_id,
            course_id=course_id,
            is_published=True
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course'] = self.object.course
        context['lessons'] = self.object.lessons.filter(is_published=True).order_by('order')
        return context

class AssignmentListView(LoginRequiredMixin, ListView):
    model = Assignment
    template_name = 'lms/assignment_list.html'
    context_object_name = 'assignments'
    paginate_by = 10
    
    def get_queryset(self):
        user = self.request.user
        profile = getattr(user, 'userprofile', None)
        
        if profile and profile.is_student:
            # Show assignments from enrolled courses
            enrolled_courses = Course.objects.filter(
                enrollments__student=user,
                enrollments__is_active=True
            )
            return Assignment.objects.filter(
                course__in=enrolled_courses,
                is_published=True
            ).order_by('due_date')
        elif profile and profile.is_faculty:
            # Show assignments from taught courses
            return Assignment.objects.filter(
                course__instructor=user,
                is_published=True
            ).order_by('due_date')
        
        return Assignment.objects.none()

class AssignmentDetailView(LoginRequiredMixin, DetailView):
    model = Assignment
    template_name = 'lms/assignment_detail.html'
    context_object_name = 'assignment'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        assignment = self.object
        user = self.request.user
        
        # Check if user has submitted
        try:
            submission = Submission.objects.get(
                assignment=assignment,
                student=user
            )
            context['submission'] = submission
        except Submission.DoesNotExist:
            context['submission'] = None
        
        return context

class SubmissionCreateView(LoginRequiredMixin, CreateView):
    model = Submission
    template_name = 'lms/submission_form.html'
    fields = ['content', 'file_upload']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['assignment'] = get_object_or_404(Assignment, pk=self.kwargs['pk'])
        return context
    
    def form_valid(self, form):
        assignment = get_object_or_404(Assignment, pk=self.kwargs['pk'])
        form.instance.assignment = assignment
        form.instance.student = self.request.user
        
        messages.success(self.request, 'Assignment submitted successfully!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return f"/lms/assignments/{self.kwargs['pk']}/"

class QuizListView(LoginRequiredMixin, ListView):
    model = Quiz
    template_name = 'lms/quiz_list.html'
    context_object_name = 'quizzes'
    
    def get_queryset(self):
        user = self.request.user
        profile = getattr(user, 'userprofile', None)
        
        if profile and profile.is_student:
            enrolled_courses = Course.objects.filter(
                enrollments__student=user,
                enrollments__is_active=True
            )
            return Quiz.objects.filter(
                course__in=enrolled_courses,
                is_published=True
            )
        elif profile and profile.is_faculty:
            return Quiz.objects.filter(
                course__instructor=user,
                is_published=True
            )
        
        return Quiz.objects.none()

class QuizDetailView(LoginRequiredMixin, DetailView):
    model = Quiz
    template_name = 'lms/quiz_detail.html'
    context_object_name = 'quiz'

class TakeQuizView(LoginRequiredMixin, TemplateView):
    template_name = 'lms/take_quiz.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        quiz = get_object_or_404(Quiz, pk=self.kwargs['pk'], is_published=True)
        context['quiz'] = quiz
        context['questions'] = quiz.questions.all().order_by('order')
        return context

class GradesView(LoginRequiredMixin, TemplateView):
    template_name = 'lms/grades.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Get submissions with grades
        submissions = (
            Submission.objects.filter(student=user, grade__isnull=False)
            .select_related('assignment', 'assignment__course')
        )

        # Add calculated percentage to each submission
        for submission in submissions:
            if submission.assignment.max_points and submission.grade is not None:
                submission.percentage = round(
                    (submission.grade / submission.assignment.max_points) * 100, 1
                )
            else:
                submission.percentage = 0.0

        context["submissions"] = submissions

        # ---- Statistics for the top cards ----
        total_assignments = submissions.count()
        average_grade = submissions.aggregate(avg=Avg("grade"))["avg"] or 0
        highest_grade = submissions.aggregate(max=Max("grade"))["max"] or 0

        context.update({
            "total_assignments": total_assignments,
            "average_grade": round(average_grade, 1),
            "highest_grade": round(highest_grade, 1),
        })

        return context