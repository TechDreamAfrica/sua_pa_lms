from django.urls import path
from . import views

app_name = 'lms'

urlpatterns = [
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('courses/', views.CourseListView.as_view(), name='course_list'),
    path('courses/<int:pk>/', views.CourseDetailView.as_view(), name='course_detail'),
    path('courses/<int:pk>/enroll/', views.EnrollCourseView.as_view(), name='enroll_course'),
    path('courses/<int:course_id>/modules/<int:module_id>/', views.ModuleDetailView.as_view(), name='module_detail'),
    path('assignments/', views.AssignmentListView.as_view(), name='assignment_list'),
    path('assignments/<int:pk>/', views.AssignmentDetailView.as_view(), name='assignment_detail'),
    path('assignments/<int:pk>/submit/', views.SubmissionCreateView.as_view(), name='assignment_submit'),
    path('quizzes/', views.QuizListView.as_view(), name='quiz_list'),
    path('quizzes/<int:pk>/', views.QuizDetailView.as_view(), name='quiz_detail'),
    path('quizzes/<int:pk>/take/', views.TakeQuizView.as_view(), name='take_quiz'),
    path('grades/', views.GradesView.as_view(), name='grades'),
]
