from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path
from django.shortcuts import redirect

from users.views import (
    login_template_view, logout_template_view,
    admin_dashboard, teacher_dashboard, student_dashboard, staff_dashboard
)


def health_check(request):
    return JsonResponse({'status': 'healthy'})


def gate_dashboard(request):
    """Redirect gate users to staff dashboard (gate users are security staff)"""
    return redirect('staff_dashboard')


def registration_dashboard(request):
    """Redirect registration users to admin dashboard"""
    return redirect('admin_dashboard')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/health/', health_check),
    path('api/', include('users.urls')),
    path('api/', include('departments.urls')),
    path('api/', include('attendance.urls')),
    path('api/monitoring/', include('monitoring.urls')),

    # Template views
    path('', login_template_view, name='login'),
    path('logout/', logout_template_view, name='logout'),
    path('admin-dashboard/', admin_dashboard, name='admin_dashboard'),
    path('teacher-dashboard/', teacher_dashboard, name='teacher_dashboard'),
    path('student-dashboard/', student_dashboard, name='student_dashboard'),
    path('staff-dashboard/', staff_dashboard, name='staff_dashboard'),
    path('gate-dashboard/', gate_dashboard, name='gate_dashboard'),
    path('registration-dashboard/', registration_dashboard, name='registration_dashboard'),
]
