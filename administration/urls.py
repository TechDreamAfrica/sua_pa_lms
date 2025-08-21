from django.urls import path
from . import views

app_name = 'administration'

urlpatterns = [
    # Dashboard
    path('', views.AdminDashboardView.as_view(), name='dashboard'),
    
    # User Management
    path('users/', views.UserManagementView.as_view(), name='user_management'),
    path('users/<int:pk>/', views.UserDetailView.as_view(), name='user_detail'),
    path('users/<int:pk>/edit/', views.UserEditView.as_view(), name='user_edit'),
    path('users/bulk-upload/', views.BulkUserUploadView.as_view(), name='bulk_user_upload'),
    path('users/export/', views.ExportUsersView.as_view(), name='export_users'),
    
    # Course Management
    path('courses/', views.CourseManagementView.as_view(), name='course_management'),
    path('courses/<int:pk>/', views.CourseDetailView.as_view(), name='course_detail'),
    path('courses/create/', views.CourseCreateView.as_view(), name='course_create'),
    path('courses/<int:pk>/edit/', views.CourseEditView.as_view(), name='course_edit'),
    path('courses/export/', views.ExportCoursesView.as_view(), name='export_courses'),
    
    # Department Management
    path('departments/', views.DepartmentManagementView.as_view(), name='department_list'),
    path('departments/create/', views.DepartmentCreateView.as_view(), name='department_create'),
    path('departments/<int:pk>/edit/', views.DepartmentEditView.as_view(), name='department_edit'),
    
    # Room Management
    path('rooms/', views.RoomManagementView.as_view(), name='room_management'),
    path('rooms/create/', views.RoomCreateView.as_view(), name='room_create'),
    path('rooms/<int:pk>/edit/', views.RoomEditView.as_view(), name='room_edit'),
    path('rooms/booking/', views.RoomBookingView.as_view(), name='room_booking'),
    
    # Maintenance Management
    path('maintenance/', views.MaintenanceManagementView.as_view(), name='maintenance_requests'),
    path('maintenance/create/', views.MaintenanceCreateView.as_view(), name='maintenance_create'),
    path('maintenance/<int:pk>/edit/', views.MaintenanceEditView.as_view(), name='maintenance_edit'),
    
    # Announcement Management
    path('announcements/', views.AnnouncementManagementView.as_view(), name='announcements'),
    path('announcements/create/', views.AnnouncementCreateView.as_view(), name='announcement_create'),
    path('announcements/<int:pk>/edit/', views.AnnouncementEditView.as_view(), name='announcement_edit'),
    
    # Reports and Analytics
    path('reports/', views.ReportsView.as_view(), name='reports'),
    
    # Attendance Management
    path('attendance/', views.AttendanceManagementView.as_view(), name='attendance_management'),
]
