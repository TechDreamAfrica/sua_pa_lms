from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import TemplateView, ListView, DetailView, CreateView
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from django.http import JsonResponse
from django.db import transaction
from .models import Timetable, DigitalID, AcademicRecord, Event, EventRegistration, Notification, LibraryResource, LibraryLoan
from .forms import AcademicRecordForm, BulkAcademicRecordUploadForm

class ServicesHomeView(LoginRequiredMixin, TemplateView):
    template_name = 'student_services/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get recent notifications
        recent_notifications = Notification.objects.filter(
            recipient=user,
            is_read=False
        )[:5]
        
        # Get upcoming events
        upcoming_events = Event.objects.filter(
            is_public=True,
            start_datetime__gte=timezone.now()
        ).order_by('start_datetime')[:3]
        
        context.update({
            'recent_notifications': recent_notifications,
            'upcoming_events': upcoming_events,
        })
        return context

class TimetableView(LoginRequiredMixin, TemplateView):
    template_name = 'student_services/timetable.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get user's timetable
        timetable = Timetable.objects.filter(student=user).order_by('day_of_week', 'start_time')
        
        context['timetable'] = timetable
        return context

class DigitalIDView(LoginRequiredMixin, TemplateView):
    template_name = 'student_services/digital_id.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get or create digital ID
        digital_id, created = DigitalID.objects.get_or_create(
            student=user,
            defaults={
                'id_number': f'UCT{user.id:06d}',
                'expiry_date': '2025-12-31'
            }
        )
        
        context['digital_id'] = digital_id
        return context

class AcademicRecordsView(LoginRequiredMixin, ListView):
    model = AcademicRecord
    template_name = 'student_services/academic_records.html'
    context_object_name = 'records'
    
    def get_queryset(self):
        return AcademicRecord.objects.filter(
            student=self.request.user
        ).select_related('course').order_by('-academic_year', '-semester')

class EventListView(LoginRequiredMixin, ListView):
    model = Event
    template_name = 'student_services/event_list.html'
    context_object_name = 'events'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Event.objects.filter(is_public=True)
        
        event_type = self.request.GET.get('type')
        search = self.request.GET.get('search')
        
        if event_type:
            queryset = queryset.filter(event_type=event_type)
        
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | 
                Q(description__icontains=search)
            )
        
        return queryset.order_by('start_datetime')

class EventDetailView(LoginRequiredMixin, DetailView):
    model = Event
    template_name = 'student_services/event_detail.html'
    context_object_name = 'event'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event = self.object
        user = self.request.user
        
        # Check if user is registered
        is_registered = EventRegistration.objects.filter(
            event=event,
            student=user
        ).exists()
        
        context['is_registered'] = is_registered
        return context

class EventRegistrationView(LoginRequiredMixin, TemplateView):
    def post(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        
        # Check if registration is required and open
        if not event.registration_required:
            messages.error(request, 'This event does not require registration.')
            return redirect('student_services:event_detail', pk=pk)
        
        # Create registration
        registration, created = EventRegistration.objects.get_or_create(
            event=event,
            student=request.user
        )
        
        if created:
            messages.success(request, f'Successfully registered for {event.title}!')
        else:
            messages.info(request, f'You are already registered for {event.title}.')
        
        return redirect('student_services:event_detail', pk=pk)

class NotificationListView(LoginRequiredMixin, ListView):
    model = Notification
    template_name = 'student_services/notifications.html'
    context_object_name = 'notifications'
    paginate_by = 20
    
    def get_queryset(self):
        return Notification.objects.filter(
            recipient=self.request.user
        ).order_by('-created_at')

class LibraryView(LoginRequiredMixin, TemplateView):
    template_name = 'student_services/library.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get featured resources
        featured_resources = LibraryResource.objects.filter(
            available_copies__gt=0
        )[:6]
        
        context['featured_resources'] = featured_resources
        return context

class LibrarySearchView(LoginRequiredMixin, ListView):
    model = LibraryResource
    template_name = 'student_services/library_search.html'
    context_object_name = 'resources'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = LibraryResource.objects.all()
        
        search = self.request.GET.get('search')
        resource_type = self.request.GET.get('type')
        
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(author__icontains=search) |
                Q(description__icontains=search)
            )
        
        if resource_type:
            queryset = queryset.filter(resource_type=resource_type)
        
        return queryset.order_by('title')

class LibraryLoansView(LoginRequiredMixin, ListView):
    model = LibraryLoan
    template_name = 'student_services/library_loans.html'
    context_object_name = 'loans'
    
    def get_queryset(self):
        return LibraryLoan.objects.filter(
            student=self.request.user
        ).select_related('resource').order_by('-borrowed_date')

# Admin-only Academic Record Management Views
class AdminRequiredMixin(UserPassesTestMixin):
    """Mixin to ensure only admin users can access the view"""
    
    def test_func(self):
        return (
            self.request.user.is_authenticated and 
            hasattr(self.request.user, 'userprofile') and 
            self.request.user.userprofile.is_admin
        )
    
    def handle_no_permission(self):
        messages.error(self.request, 'You do not have permission to access this page.')
        return redirect('student_services:home')

class AcademicRecordManagementView(AdminRequiredMixin, TemplateView):
    """Main view for academic record management"""
    template_name = 'student_services/admin/academic_records_management.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get recent academic records
        recent_records = AcademicRecord.objects.select_related(
            'student', 'course'
        ).order_by('-created_at')[:10]
        
        # Get statistics
        total_records = AcademicRecord.objects.count()
        total_students = AcademicRecord.objects.values('student').distinct().count()
        
        context.update({
            'recent_records': recent_records,
            'total_records': total_records,
            'total_students': total_students,
        })
        return context

class AddAcademicRecordView(AdminRequiredMixin, CreateView):
    """View for adding single academic record"""
    model = AcademicRecord
    form_class = AcademicRecordForm
    template_name = 'student_services/admin/add_academic_record.html'
    
    def form_valid(self, form):
        messages.success(self.request, 'Academic record added successfully!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return '/student-services/admin/academic-records/'

class BulkUploadAcademicRecordsView(AdminRequiredMixin, TemplateView):
    """View for bulk upload of academic records via CSV"""
    template_name = 'student_services/admin/bulk_upload_academic_records.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = BulkAcademicRecordUploadForm()
        return context
    
    def post(self, request, *args, **kwargs):
        form = BulkAcademicRecordUploadForm(request.POST, request.FILES)
        
        if form.is_valid():
            try:
                # Process CSV and get records to create
                records_to_create = form.process_csv(
                    course=form.cleaned_data['course'],
                    semester=form.cleaned_data['semester'],
                    academic_year=form.cleaned_data['academic_year']
                )
                
                # Create records in a transaction
                with transaction.atomic():
                    created_records = AcademicRecord.objects.bulk_create(records_to_create)
                
                messages.success(
                    request, 
                    f'Successfully uploaded {len(created_records)} academic records!'
                )
                return redirect('student_services:academic_records_management')
                
            except Exception as e:
                messages.error(request, f'Error processing upload: {str(e)}')
        
        return self.render_to_response({'form': form})

class AcademicRecordsListView(AdminRequiredMixin, ListView):
    """View for listing and managing academic records"""
    model = AcademicRecord
    template_name = 'student_services/admin/academic_records_list.html'
    context_object_name = 'records'
    paginate_by = 25
    
    def get_queryset(self):
        queryset = AcademicRecord.objects.select_related(
            'student', 'course'
        ).order_by('-created_at')
        
        # Apply filters
        search = self.request.GET.get('search')
        course = self.request.GET.get('course')
        semester = self.request.GET.get('semester')
        academic_year = self.request.GET.get('academic_year')
        
        if search:
            queryset = queryset.filter(
                Q(student__first_name__icontains=search) |
                Q(student__last_name__icontains=search) |
                Q(student__username__icontains=search) |
                Q(course__title__icontains=search) |
                Q(course__code__icontains=search)
            )
        
        if course:
            queryset = queryset.filter(course_id=course)
        
        if semester:
            queryset = queryset.filter(semester=semester)
        
        if academic_year:
            queryset = queryset.filter(academic_year=academic_year)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add filter options
        from lms.models import Course
        context['courses'] = Course.objects.all().order_by('title')
        context['semesters'] = ['fall', 'spring', 'summer', 'winter']
        context['academic_years'] = AcademicRecord.objects.values_list(
            'academic_year', flat=True
        ).distinct().order_by('-academic_year')
        
        # Preserve filter values
        context['current_filters'] = {
            'search': self.request.GET.get('search', ''),
            'course': self.request.GET.get('course', ''),
            'semester': self.request.GET.get('semester', ''),
            'academic_year': self.request.GET.get('academic_year', ''),
        }
        
        return context

class DownloadSampleCSVView(AdminRequiredMixin, TemplateView):
    """View to download a sample CSV template"""
    
    def get(self, request, *args, **kwargs):
        from django.http import HttpResponse
        import csv
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="academic_records_template.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['student_id', 'grade', 'grade_points', 'credits_earned'])
        writer.writerow(['student123', 'A', '3.7', '3'])
        writer.writerow(['student456', 'B+', '3.0', '4'])
        writer.writerow(['student789', 'A-', '3.3', '3'])
        
        return response
