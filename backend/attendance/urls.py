from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import (
    AttendanceViewSet, ScheduleViewSet,
    schedule_today, attendance_face_summary,
    attendance_face_checkin, attendance_face_attempts
)

router = SimpleRouter()
router.register(r'attendance', AttendanceViewSet, basename='attendance')
router.register(r'schedule', ScheduleViewSet, basename='schedule')

urlpatterns = [
    path('', include(router.urls)),
    
    # Gate portal endpoints
    path('schedule/today/', schedule_today, name='schedule-today'),
    path('attendance/face-summary/', attendance_face_summary, name='attendance-face-summary'),
    path('attendance/face-checkin/', attendance_face_checkin, name='attendance-face-checkin'),
    path('attendance/face-attempts/', attendance_face_attempts, name='attendance-face-attempts'),
]
