from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.db.models import Count, Q, Avg
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.db import transaction
from django.core.paginator import Paginator
from datetime import datetime, timedelta
import csv
from .models import Department, Room, RoomBooking, AttendanceRecord, SystemReport, MaintenanceRequest, Announcement
from lms.models import Course, Enrollment, Assignment, Submission
from student_services.models import AcademicRecord, Event
from accounts.models import UserProfile
from .forms import (
    UserEditForm, UserProfileEditForm, DepartmentForm, RoomForm, MaintenanceRequestForm, 
    AnnouncementForm, SystemReportForm, BulkUserUploadForm
)

class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return hasattr(self.request.user, 'userprofile') and self.request.user.userprofile.is_admin

class AdminDashboardView(LoginRequiredMixin, AdminRequiredMixin, TemplateView):
    template_name = 'administration/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

class CourseManagementView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    model = Course
    template_name = 'administration/course_management.html'
    context_object_name = 'courses'
    paginate_by = 10

    def get_queryset(self):
        queryset = Course.objects.all().order_by('code')
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(code__icontains=search_query) |
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_courses'] = Course.objects.count()
        return context
        
        # Get comprehensive admin dashboard stats
        total_users = User.objects.count()
        total_courses = Course.objects.count()
        total_departments = Department.objects.count()
        pending_maintenance = MaintenanceRequest.objects.filter(status='pending').count()
        
        # Student statistics
        student_count = User.objects.filter(userprofile__user_type='student').count()
        faculty_count = User.objects.filter(userprofile__user_type='faculty').count()
        admin_count = User.objects.filter(userprofile__user_type='admin').count()
        
        # Course statistics
        active_courses = Course.objects.filter(is_active=True).count()
        total_enrollments = Enrollment.objects.count()
        
        # Recent activity
        recent_users = User.objects.order_by('-date_joined')[:5]
        recent_courses = Course.objects.order_by('-created_at')[:5]
        recent_maintenance = MaintenanceRequest.objects.order_by('-created_at')[:5]
        
        context.update({
            'total_users': total_users,
            'total_courses': total_courses,
            'total_departments': total_departments,
            'pending_maintenance': pending_maintenance,
            'student_count': student_count,
            'faculty_count': faculty_count,
            'admin_count': admin_count,
            'active_courses': active_courses,
            'total_enrollments': total_enrollments,
            'recent_users': recent_users,
            'recent_courses': recent_courses,
            'recent_maintenance': recent_maintenance,
        })
        return context

class UserManagementView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    model = User
    template_name = 'administration/user_management.html'
    context_object_name = 'users'
    paginate_by = 25
    
    def get_queryset(self):
        queryset = User.objects.select_related('userprofile')
        
        search = self.request.GET.get('search')
        user_type = self.request.GET.get('type')
        department = self.request.GET.get('department')
        is_active = self.request.GET.get('is_active')
        
        if search:
            queryset = queryset.filter(
                Q(username__icontains=search) |
                Q(email__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(userprofile__student_id__icontains=search) |
                Q(userprofile__employee_id__icontains=search)
            )
        
        if user_type:
            queryset = queryset.filter(userprofile__user_type=user_type)
        
        if department:
            queryset = queryset.filter(userprofile__department=department)
        
        if is_active:
            queryset = queryset.filter(is_active=is_active == 'true')
        
        return queryset.order_by('username')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['departments'] = Department.objects.all()
        context['user_types'] = [
            ('student', 'Student'),
            ('faculty', 'Faculty'),
            ('admin', 'Administrator'),
        ]
        # Preserve filter values
        context['current_filters'] = {
            'search': self.request.GET.get('search', ''),
            'type': self.request.GET.get('type', ''),
            'department': self.request.GET.get('department', ''),
            'is_active': self.request.GET.get('is_active', ''),
        }
        return context

class UserDetailView(LoginRequiredMixin, AdminRequiredMixin, DetailView):
    model = User
    template_name = 'administration/user_detail.html'
    context_object_name = 'user_obj'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.object
        
        # Get user's academic records if student
        if hasattr(user, 'userprofile') and user.userprofile.is_student:
            context['academic_records'] = AcademicRecord.objects.filter(
                student=user
            ).select_related('course').order_by('-academic_year', '-semester')
            
            # Calculate GPA
            records = context['academic_records']
            if records:
                total_points = sum(record.grade_points * record.credits_earned for record in records)
                total_credits = sum(record.credits_earned for record in records)
                context['gpa'] = round(total_points / total_credits, 2) if total_credits > 0 else 0
        
        # Get courses taught if faculty
        if hasattr(user, 'userprofile') and user.userprofile.is_faculty:
            context['taught_courses'] = Course.objects.filter(instructor=user)
        
        # Get enrollments if student
        if hasattr(user, 'userprofile') and user.userprofile.is_student:
            context['enrollments'] = Enrollment.objects.filter(
                student=user
            ).select_related('course')
        
        return context

class UserEditView(LoginRequiredMixin, AdminRequiredMixin, TemplateView):
    template_name = 'administration/user_edit.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = get_object_or_404(User, pk=kwargs['pk'])
        profile, created = UserProfile.objects.get_or_create(user=user)
        
        context['user_obj'] = user
        context['user_form'] = UserEditForm(instance=user)
        context['profile_form'] = UserProfileEditForm(instance=profile)
        return context
    
    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        profile, created = UserProfile.objects.get_or_create(user=user)
        
        user_form = UserEditForm(request.POST, instance=user)
        profile_form = UserProfileEditForm(request.POST, instance=profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, f'User {user.username} updated successfully!')
            return redirect('administration:user_detail', pk=pk)
        
        context = {
            'user_obj': user,
            'user_form': user_form,
            'profile_form': profile_form,
        }
        return render(request, self.template_name, context)

class BulkUserUploadView(LoginRequiredMixin, AdminRequiredMixin, TemplateView):
    template_name = 'administration/bulk_user_upload.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = BulkUserUploadForm()
        return context
    
    def post(self, request):
        form = BulkUserUploadForm(request.POST, request.FILES)
        
        if form.is_valid():
            try:
                users_data = form.process_csv()
                
                with transaction.atomic():
                    created_users = []
                    for user_data in users_data:
                        user_type = user_data.pop('user_type')
                        
                        # Create user
                        user = User.objects.create_user(
                            password='temppass123',  # Temporary password
                            **user_data
                        )
                        
                        # Create profile
                        UserProfile.objects.create(
                            user=user,
                            user_type=user_type
                        )
                        
                        created_users.append(user)
                
                messages.success(
                    request,
                    f'Successfully created {len(created_users)} users! '
                    f'Temporary password: temppass123'
                )
                return redirect('administration:user_management')
                
            except Exception as e:
                messages.error(request, f'Error processing upload: {str(e)}')
        
        return render(request, self.template_name, {'form': form})

# Enhanced Course Management Views
class CourseManagementView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    model = Course
    template_name = 'administration/course_management.html'
    context_object_name = 'courses'
    paginate_by = 25
    
    def get_queryset(self):
        queryset = Course.objects.select_related('instructor', 'department')
        
        search = self.request.GET.get('search')
        department = self.request.GET.get('department')
        level = self.request.GET.get('level')
        is_active = self.request.GET.get('is_active')
        
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(code__icontains=search) |
                Q(instructor__first_name__icontains=search) |
                Q(instructor__last_name__icontains=search)
            )
        
        if department:
            queryset = queryset.filter(department=department)
        
        if level:
            queryset = queryset.filter(level=level)
        
        if is_active:
            queryset = queryset.filter(is_active=is_active == 'true')
        
        return queryset.order_by('code')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['departments'] = Department.objects.all()
        context['levels'] = Course.LEVEL_CHOICES if hasattr(Course, 'LEVEL_CHOICES') else []
        context['current_filters'] = {
            'search': self.request.GET.get('search', ''),
            'department': self.request.GET.get('department', ''),
            'level': self.request.GET.get('level', ''),
            'is_active': self.request.GET.get('is_active', ''),
        }
        return context

class CourseCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = Course
    template_name = 'administration/course_form.html'
    fields = ['code', 'title', 'description', 'department', 'instructor', 'credits', 'is_active']
    success_url = '/administration/courses/'
    
    def form_valid(self, form):
        messages.success(self.request, 'Course created successfully!')
        return super().form_valid(form)
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Add CSS classes to form fields
        for field in form.fields.values():
            field.widget.attrs.update({
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-uct-blue focus:ring-uct-blue sm:text-sm'
            })
        
        # Filter instructor to only faculty
        form.fields['instructor'].queryset = User.objects.filter(
            userprofile__user_type='faculty'
        )
        return form

class CourseEditView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    model = Course
    template_name = 'administration/course_form.html'
    fields = ['code', 'title', 'description', 'department', 'instructor', 'credits', 'is_active']
    success_url = '/administration/courses/'
    
    def form_valid(self, form):
        messages.success(self.request, 'Course updated successfully!')
        return super().form_valid(form)
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Add CSS classes to form fields
        for field in form.fields.values():
            field.widget.attrs.update({
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-uct-blue focus:ring-uct-blue sm:text-sm'
            })
        
        # Filter instructor to only faculty
        form.fields['instructor'].queryset = User.objects.filter(
            userprofile__user_type='faculty'
        )
        return form

class CourseDetailView(LoginRequiredMixin, AdminRequiredMixin, DetailView):
    model = Course
    template_name = 'administration/course_detail.html'
    context_object_name = 'course'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.object
        
        # Get enrollment statistics
        enrollments = Enrollment.objects.filter(course=course)
        context['total_enrollments'] = enrollments.count()
        context['enrollments'] = enrollments.select_related('student')[:10]
        
        # Get assignments
        context['assignments'] = Assignment.objects.filter(course=course).order_by('-due_date')[:5]
        
        # Get academic records
        context['academic_records'] = AcademicRecord.objects.filter(
            course=course
        ).select_related('student').order_by('-created_at')[:10]
        
        return context

# Department Management Views
class DepartmentManagementView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    model = Department
    template_name = 'administration/department_management.html'
    context_object_name = 'departments'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add statistics for each department
        departments_with_stats = []
        for dept in context['departments']:
            stats = {
                'department': dept,
                'faculty_count': User.objects.filter(userprofile__department=dept.code, userprofile__user_type='faculty').count(),
                'student_count': User.objects.filter(userprofile__department=dept.code, userprofile__user_type='student').count(),
                'course_count': Course.objects.filter(department=dept).count(),
            }
            departments_with_stats.append(stats)
        context['departments_with_stats'] = departments_with_stats
        return context

class DepartmentCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = Department
    form_class = DepartmentForm
    template_name = 'administration/department_form.html'
    success_url = '/admin-panel/departments'
    
    def form_valid(self, form):
        messages.success(self.request, 'Department created successfully!')
        return super().form_valid(form)

class DepartmentEditView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    model = Department
    form_class = DepartmentForm
    template_name = 'administration/department_form.html'
    success_url = '/admin-panel/departments/'
    
    def form_valid(self, form):
        messages.success(self.request, 'Department updated successfully!')
        return super().form_valid(form)

# Room Management Views
class RoomManagementView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    model = Room
    template_name = 'administration/room_management.html'
    context_object_name = 'rooms'
    paginate_by = 25
    
    def get_queryset(self):
        queryset = Room.objects.all()
        
        search = self.request.GET.get('search')
        building = self.request.GET.get('building')
        room_type = self.request.GET.get('room_type')
        is_available = self.request.GET.get('is_available')
        
        if search:
            queryset = queryset.filter(
                Q(number__icontains=search) |
                Q(building__icontains=search) |
                Q(equipment__icontains=search)
            )
        
        if building:
            queryset = queryset.filter(building=building)
        
        if room_type:
            queryset = queryset.filter(room_type=room_type)
        
        if is_available:
            queryset = queryset.filter(is_available=is_available == 'true')
        
        return queryset.order_by('building', 'number')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['buildings'] = Room.objects.values_list('building', flat=True).distinct()
        context['room_types'] = Room.ROOM_TYPE_CHOICES if hasattr(Room, 'ROOM_TYPE_CHOICES') else []
        context['current_filters'] = {
            'search': self.request.GET.get('search', ''),
            'building': self.request.GET.get('building', ''),
            'room_type': self.request.GET.get('room_type', ''),
            'is_available': self.request.GET.get('is_available', ''),
        }
        return context

class RoomCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = Room
    form_class = RoomForm
    template_name = 'administration/room_form.html'
    success_url = '/administration/rooms/'
    
    def form_valid(self, form):
        messages.success(self.request, 'Room created successfully!')
        return super().form_valid(form)

class RoomEditView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    model = Room
    form_class = RoomForm
    template_name = 'administration/room_form.html'
    success_url = '/administration/rooms/'
    
    def form_valid(self, form):
        messages.success(self.request, 'Room updated successfully!')
        return super().form_valid(form)

# Maintenance Management Views
class MaintenanceManagementView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    model = MaintenanceRequest
    template_name = 'administration/maintenance_management.html'
    context_object_name = 'requests'
    paginate_by = 25
    
    def get_queryset(self):
        queryset = MaintenanceRequest.objects.select_related('requested_by', 'assigned_to')
        
        status = self.request.GET.get('status')
        priority = self.request.GET.get('priority')
        search = self.request.GET.get('search')
        
        if status:
            queryset = queryset.filter(status=status)
        
        if priority:
            queryset = queryset.filter(priority=priority)
        
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(location__icontains=search) |
                Q(description__icontains=search)
            )
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = MaintenanceRequest.STATUS_CHOICES if hasattr(MaintenanceRequest, 'STATUS_CHOICES') else []
        context['priority_choices'] = MaintenanceRequest.PRIORITY_CHOICES if hasattr(MaintenanceRequest, 'PRIORITY_CHOICES') else []
        context['current_filters'] = {
            'status': self.request.GET.get('status', ''),
            'priority': self.request.GET.get('priority', ''),
            'search': self.request.GET.get('search', ''),
        }
        return context

class MaintenanceCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = MaintenanceRequest
    form_class = MaintenanceRequestForm
    template_name = 'administration/maintenance_form.html'
    success_url = '/administration/maintenance/'
    
    def form_valid(self, form):
        form.instance.requested_by = self.request.user
        messages.success(self.request, 'Maintenance request created successfully!')
        return super().form_valid(form)

class MaintenanceEditView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    model = MaintenanceRequest
    form_class = MaintenanceRequestForm
    template_name = 'administration/maintenance_form.html'
    success_url = '/administration/maintenance/'
    
    def form_valid(self, form):
        messages.success(self.request, 'Maintenance request updated successfully!')
        return super().form_valid(form)

# Announcement Management Views
class AnnouncementManagementView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    model = Announcement
    template_name = 'administration/announcement_management.html'
    context_object_name = 'announcements'
    paginate_by = 25
    
    def get_queryset(self):
        return Announcement.objects.select_related('created_by').order_by('-created_at')

class AnnouncementCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = Announcement
    form_class = AnnouncementForm
    template_name = 'administration/announcement_form.html'
    success_url = '/administration/announcements/'
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, 'Announcement created successfully!')
        return super().form_valid(form)

class AnnouncementEditView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    model = Announcement
    form_class = AnnouncementForm
    template_name = 'administration/announcement_form.html'
    success_url = '/administration/announcements/'
    
    def form_valid(self, form):
        messages.success(self.request, 'Announcement updated successfully!')
        return super().form_valid(form)

# Reports and Analytics Views
class ReportsView(LoginRequiredMixin, AdminRequiredMixin, TemplateView):
    template_name = 'administration/reports.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Generate comprehensive reports
        context.update({
            # User statistics
            'total_users': User.objects.count(),
            'active_users': User.objects.filter(is_active=True).count(),
            'students_count': User.objects.filter(userprofile__user_type='student').count(),
            'faculty_count': User.objects.filter(userprofile__user_type='faculty').count(),
            'admin_count': User.objects.filter(userprofile__user_type='admin').count(),
            
            # Course statistics
            'total_courses': Course.objects.count(),
            'active_courses': Course.objects.filter(is_active=True).count(),
            'total_enrollments': Enrollment.objects.count(),
            
            # Academic performance
            'total_academic_records': AcademicRecord.objects.count(),
            'average_gpa': AcademicRecord.objects.aggregate(Avg('grade_points'))['grade_points__avg'] or 0,
            
            # System usage
            'recent_logins': User.objects.filter(last_login__gte=timezone.now() - timedelta(days=30)).count(),
            'pending_maintenance': MaintenanceRequest.objects.filter(status='pending').count(),
            'total_announcements': Announcement.objects.filter(is_published=True).count(),
        })
        return context

# Data Export Views
class ExportUsersView(LoginRequiredMixin, AdminRequiredMixin, TemplateView):
    def get(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="users_export.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Username', 'First Name', 'Last Name', 'Email', 'User Type', 'Department', 'Is Active', 'Date Joined'])
        
        users = User.objects.select_related('userprofile').all()
        for user in users:
            profile = getattr(user, 'userprofile', None)
            writer.writerow([
                user.username,
                user.first_name,
                user.last_name,
                user.email,
                profile.get_user_type_display() if profile else 'N/A',
                profile.get_department_display() if profile and profile.department else 'N/A',
                'Yes' if user.is_active else 'No',
                user.date_joined.strftime('%Y-%m-%d')
            ])
        
        return response

class ExportCoursesView(LoginRequiredMixin, AdminRequiredMixin, TemplateView):
    def get(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="courses_export.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Code', 'Title', 'Instructor', 'Department', 'Credits', 'Enrollments', 'Is Active'])
        
        courses = Course.objects.select_related('instructor', 'department').all()
        for course in courses:
            enrollment_count = Enrollment.objects.filter(course=course).count()
            writer.writerow([
                course.code,
                course.title,
                course.instructor.get_full_name() if course.instructor else 'N/A',
                course.department.name if course.department else 'N/A',
                course.credits,
                enrollment_count,
                'Yes' if course.is_active else 'No'
            ])
        
        return response

# Additional Management Views
class RoomBookingView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    model = RoomBooking
    template_name = 'administration/room_booking.html'
    context_object_name = 'bookings'
    paginate_by = 25
    
    def get_queryset(self):
        queryset = RoomBooking.objects.select_related('room', 'booked_by')
        
        room = self.request.GET.get('room')
        status = self.request.GET.get('status')
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')
        
        if room:
            queryset = queryset.filter(room=room)
        
        if status == 'approved':
            queryset = queryset.filter(is_approved=True)
        elif status == 'pending':
            queryset = queryset.filter(is_approved=False)
        
        if date_from:
            queryset = queryset.filter(start_datetime__date__gte=date_from)
        
        if date_to:
            queryset = queryset.filter(start_datetime__date__lte=date_to)
        
        return queryset.order_by('-start_datetime')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['rooms'] = Room.objects.all()
        context['current_filters'] = {
            'room': self.request.GET.get('room', ''),
            'status': self.request.GET.get('status', ''),
            'date_from': self.request.GET.get('date_from', ''),
            'date_to': self.request.GET.get('date_to', ''),
        }
        return context

class AttendanceManagementView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    model = AttendanceRecord
    template_name = 'administration/attendance_management.html'
    context_object_name = 'attendance_records'
    paginate_by = 25
    
    def get_queryset(self):
        queryset = AttendanceRecord.objects.select_related('student', 'course', 'marked_by')
        
        course = self.request.GET.get('course')
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')
        is_present = self.request.GET.get('is_present')
        
        if course:
            queryset = queryset.filter(course=course)
        
        if date_from:
            queryset = queryset.filter(date__gte=date_from)
        
        if date_to:
            queryset = queryset.filter(date__lte=date_to)
        
        if is_present:
            queryset = queryset.filter(is_present=is_present == 'true')
        
        return queryset.order_by('-date', 'course__code')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['courses'] = Course.objects.all()
        context['current_filters'] = {
            'course': self.request.GET.get('course', ''),
            'date_from': self.request.GET.get('date_from', ''),
            'date_to': self.request.GET.get('date_to', ''),
            'is_present': self.request.GET.get('is_present', ''),
        }
        return context
