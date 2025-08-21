from django.contrib import admin
from django.urls import path
from . import views
urlpatterns = [
    path('admin/', admin.site.urls),  # Default Django admin
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),  # Custom admin dashboard

    path('', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.custom_logout, name='logout'),

    # Dashboards
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('faculty/dashboard/', views.faculty_dashboard, name='faculty_dashboard'),

    # Apply Leave
    path('student/apply_leave/', views.apply_leave, name='apply_leave'),

    path('leave/<int:pk>/', views.leave_detail, name='leave_detail'),
    path('leave/<int:pk>/approve/', views.approve_leave, name='approve_leave'),
    path('leave/<int:pk>/reject/', views.reject_leave, name='reject_leave'),

    path('admin/settings/', views.admin_settings, name='admin_settings'),
    #path('admin/departments/', views.admin_departments, name='admin_departments'),  # ✅ FIXED
]
