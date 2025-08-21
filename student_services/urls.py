from django.urls import path
from . import views

app_name = 'student_services'

urlpatterns = [
    path('', views.ServicesHomeView.as_view(), name='home'),
    path('timetable/', views.TimetableView.as_view(), name='timetable'),
    path('digital-id/', views.DigitalIDView.as_view(), name='digital_id'),
    path('academic-records/', views.AcademicRecordsView.as_view(), name='academic_records'),
    path('events/', views.EventListView.as_view(), name='event_list'),
    path('events/<int:pk>/', views.EventDetailView.as_view(), name='event_detail'),
    path('events/<int:pk>/register/', views.EventRegistrationView.as_view(), name='event_register'),
    path('notifications/', views.NotificationListView.as_view(), name='notifications'),
    path('library/', views.LibraryView.as_view(), name='library'),
    path('library/search/', views.LibrarySearchView.as_view(), name='library_search'),
    path('library/loans/', views.LibraryLoansView.as_view(), name='library_loans'),
    
    # Admin-only Academic Record Management URLs
    path('admin/academic-records/', views.AcademicRecordManagementView.as_view(), name='academic_records_management'),
    path('admin/academic-records/add/', views.AddAcademicRecordView.as_view(), name='add_academic_record'),
    path('admin/academic-records/bulk-upload/', views.BulkUploadAcademicRecordsView.as_view(), name='bulk_upload_academic_records'),
    path('admin/academic-records/list/', views.AcademicRecordsListView.as_view(), name='academic_records_list'),
    path('admin/academic-records/download-sample/', views.DownloadSampleCSVView.as_view(), name='download_sample_csv'),
]
