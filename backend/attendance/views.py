from rest_framework import viewsets, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from django.utils import timezone
from datetime import datetime, timedelta

from users.permissions import IsSuperAdminOrReadOnly

from .models import Attendance, Schedule
from .serializers import AttendanceSerializer, ScheduleSerializer


class AttendanceViewSet(viewsets.ModelViewSet):
    """Attendance is private per person: students see their own record, a super
    admin sees everything, a teacher sees only lectures they teach.
    
    SECURITY: Only super admins can edit or delete attendance records.
    Teachers can only create new records. Students can only read their own records."""

    serializer_class = AttendanceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = Attendance.objects.select_related('person')
        if user.is_super_admin:
            return qs
        if user.user_type == user.UserType.TEACHER:
            return qs.filter(
                person__taught_classes__in=user.taught_classes.all()).distinct()
        return qs.filter(person=user)

    def get_permissions(self):
        """Lock edit/delete operations to super admins only"""
        if self.action in ['update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsSuperAdminOrReadOnly()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        user = self.request.user
        person = serializer.validated_data.get('person')

        if user.is_super_admin:
            serializer.save(recorded_by=user)
            return
        if user.user_type != user.UserType.TEACHER:
            raise PermissionDenied('تسجيل الحضور يتطلب صلاحيات المدرس أو المشرف.')
        if person is None or not self._teacher_shares_class(user, person):
            raise PermissionDenied('لا يمكنك تسجيل حضور من خارج محاضراتك.')
        serializer.save(recorded_by=user)

    def perform_update(self, serializer):
        """Only super admins can update attendance records"""
        if not self.request.user.is_super_admin:
            raise PermissionDenied('تعديل سجلات الحضور متاح للمشرفين فقط.')
        serializer.save()

    def perform_destroy(self, instance):
        """Only super admins can delete attendance records"""
        if not self.request.user.is_super_admin:
            raise PermissionDenied('حذف سجلات الحضور متاح للمشرفين فقط.')
        instance.delete()

    @staticmethod
    def _teacher_shares_class(teacher, person):
        """A teacher may record only members of a class they actually teach:
        every schedule dimension the teacher holds must match the person."""
        for schedule in teacher.taught_classes.all():
            if person.department_id != schedule.department_id:
                continue
            if person.stage_id != schedule.stage_id:
                continue
            if person.branch_id != schedule.branch_id:
                continue
            return True
        return False


class ScheduleViewSet(viewsets.ModelViewSet):
    serializer_class = ScheduleSerializer
    permission_classes = [IsSuperAdminOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        qs = Schedule.objects.select_related('teacher', 'department', 'stage', 'branch')
        if user.is_super_admin:
            return qs
        if user.user_type == user.UserType.TEACHER:
            return qs.filter(teacher=user)
        return qs


# ============ Gate Portal API Endpoints ============

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def schedule_today(request):
    """Get today's schedules for gate portal"""
    from users.models import User
    
    today = timezone.now().date()
    day_name = today.strftime('%A').lower()
    
    # Map English day names to Arabic choices
    day_mapping = {
        'sunday': 'الأحد',
        'monday': 'الاثنين',
        'tuesday': 'الثلاثاء',
        'wednesday': 'الأربعاء',
        'thursday': 'الخميس',
        'friday': 'الجمعة',
        'saturday': 'السبت',
    }
    
    arabic_day = day_mapping.get(day_name, day_name)
    
    schedules = Schedule.objects.filter(day=arabic_day).select_related(
        'teacher', 'department', 'stage', 'branch'
    )
    
    server_time = timezone.now().strftime('%H:%M:%S')
    
    results = []
    for schedule in schedules:
        # Calculate phase (open, before_open, closed)
        # For now, simple logic: all schedules are "open"
        results.append({
            'id': schedule.id,
            'subject': schedule.subject,
            'time': str(schedule.time),
            'day': schedule.day,
            'teacher': schedule.teacher.name,
            'department': schedule.department.name if schedule.department else None,
            'stage': schedule.stage.name if schedule.stage else None,
            'branch': schedule.branch.name if schedule.branch else None,
            'phase': 'open',  # Simplified for now
            'open_from': '00:00',  # Simplified
            'open_until': '23:59',  # Simplified
            'already_recorded': False,  # Would need to check attendance
        })
    
    return Response({
        'day': today.strftime('%Y-%m-%d'),
        'server_time': server_time,
        'results': results
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def attendance_face_summary(request):
    """Get face attendance summary for today"""
    today = timezone.now().date()
    
    # Count attendance by status
    attendance_qs = Attendance.objects.filter(date=today)
    present = attendance_qs.filter(status='present').count()
    late = attendance_qs.filter(status='late').count()
    absent = attendance_qs.filter(status='absent').count()
    
    # For now, simplified counts
    return Response({
        'date': today.strftime('%Y-%m-%d'),
        'present': present,
        'late': late,
        'absent': absent,
        'face_records': present + late,  # Simplified
        'manual_records': 0,  # Would need manual flag
        'unknown_faces': 0,  # Would need face attempt tracking
        'invalid_samples': 0,
    })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def attendance_face_checkin(request):
    """Face check-in endpoint for gate portal"""
    from users.models import User
    from users.views import recognize_face
    import numpy as np
    
    embedding = request.data.get('embedding')
    schedule_id = request.data.get('schedule')
    location = request.data.get('location', 'البوابة الرئيسية')
    
    if not embedding or not schedule_id:
        return Response({'error': 'Embedding and schedule required'}, status=400)
    
    if len(embedding) != 128:
        return Response({'error': 'Embedding must be 128-dimensional'}, status=400)
    
    # Get schedule
    try:
        schedule = Schedule.objects.get(pk=schedule_id)
    except Schedule.DoesNotExist:
        return Response({'error': 'Schedule not found'}, status=404)
    
    # Try to recognize face
    from users.models import FaceSample
    
    best_match = None
    best_distance = float('inf')
    
    samples = FaceSample.objects.select_related('profile__person').all()
    for sample in samples:
        sample_embedding = sample.embedding
        if sample_embedding and len(sample_embedding) == 128:
            distance = np.sqrt(sum((a - b) ** 2 for a, b in zip(embedding, sample_embedding)))
            if distance < best_distance:
                best_distance = distance
                best_match = sample
    
    threshold = 0.6
    if not best_match or best_distance >= threshold:
        return Response({
            'matched': False,
            'saved': False,
            'reason': 'وجه غير معروف'
        })
    
    person = best_match.profile.person
    
    # Check if attendance already recorded for this person today and schedule
    today = timezone.now().date()
    existing = Attendance.objects.filter(
        person=person,
        date=today,
        location=location
    ).first()
    
    if existing:
        return Response({
            'matched': True,
            'saved': False,
            'created': False,
            'person': {
                'id': person.id,
                'name': person.name,
                'user_type': person.user_type,
                'code': person.code
            },
            'attendance': {
                'id': existing.id,
                'status': existing.status,
                'time': str(existing.time)
            },
            'reason': 'الحضور مسجل مسبقاً'
        })
    
    # Create attendance record
    now = timezone.now()
    attendance = Attendance.objects.create(
        person=person,
        date=today,
        time=now.time(),
        status='present',  # Simplified, could calculate late based on schedule time
        location=location,
        recorded_by=request.user
    )
    
    return Response({
        'matched': True,
        'saved': True,
        'created': True,
        'operation_id': str(attendance.id),  # Simplified
        'person': {
            'id': person.id,
            'name': person.name,
            'user_type': person.user_type,
            'code': person.code
        },
        'attendance': {
            'id': attendance.id,
            'status': attendance.status,
            'time': str(attendance.time)
        }
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def attendance_face_attempts(request):
    """Get face recognition attempts log (simplified version)"""
    today = request.query_params.get('today') == '1'
    limit = int(request.query_params.get('limit', 30))
    
    # For now, return attendance records as a proxy for face attempts
    # In a full implementation, this would query a FaceMatchAttempt model
    qs = Attendance.objects.select_related('person').order_by('-created_at')
    
    if today:
        today_date = timezone.now().date()
        qs = qs.filter(date=today_date)
    
    qs = qs[:limit]
    
    results = []
    for record in qs:
        results.append({
            'created_at': record.created_at.isoformat(),
            'result': 'matched',  # Simplified
            'result_display': 'تم التعرف',
            'best_distance': 0.0,  # Simplified
            'person': record.person.name if record.person else 'غير معروف'
        })
    
    return Response({
        'results': results
    })
