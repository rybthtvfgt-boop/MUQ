from django.conf import settings
from django.db import models


class Attendance(models.Model):
    """Class-session attendance. Gate entry/exit events are a separate model in
    Phase 4 — a person may pass a gate many times per day."""

    STATUS_CHOICES = [
        ('present', 'حاضر'),
        ('absent', 'غائب'),
        ('late', 'متأخر'),
    ]

    person = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='attendance_records', verbose_name='الشخص')
    date = models.DateField(verbose_name='التاريخ')
    time = models.TimeField(verbose_name='الوقت')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, verbose_name='الحالة')
    location = models.CharField(max_length=200, default='البوابة الرئيسية', verbose_name='الموقع')
    notes = models.TextField(blank=True, verbose_name='ملاحظات')
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='attendance_recorded', verbose_name='سجّلها')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ التسجيل')

    class Meta:
        verbose_name = 'سجل حضور'
        verbose_name_plural = 'سجلات الحضور'
        constraints = [
            models.UniqueConstraint(
                fields=['person', 'date', 'time'], name='unique_person_date_time'),
        ]
        indexes = [models.Index(fields=['person', 'date'])]

    def __str__(self):
        return f'{self.person.name} - {self.date} ({self.get_status_display()})'


class Schedule(models.Model):
    DAY_CHOICES = [
        ('sunday', 'الأحد'), ('monday', 'الاثنين'), ('tuesday', 'الثلاثاء'),
        ('wednesday', 'الأربعاء'), ('thursday', 'الخميس'), ('friday', 'الجمعة'),
        ('saturday', 'السبت'),
    ]

    day = models.CharField(max_length=10, choices=DAY_CHOICES, verbose_name='اليوم')
    time = models.TimeField(verbose_name='الوقت')
    subject = models.CharField(max_length=200, verbose_name='المادة')
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='taught_classes', verbose_name='المدرس')
    department = models.ForeignKey(
        'departments.Department', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='schedules', verbose_name='القسم')
    stage = models.ForeignKey(
        'departments.Stage', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='schedules', verbose_name='المرحلة')
    branch = models.ForeignKey(
        'departments.Branch', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='schedules', verbose_name='الشعبة')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')

    class Meta:
        verbose_name = 'جدول دراسي'
        verbose_name_plural = 'الجداول الدراسية'
        constraints = [
            models.UniqueConstraint(
                fields=['day', 'time', 'teacher'], name='unique_teacher_slot'),
        ]

    def __str__(self):
        return f'{self.day} - {self.time} - {self.subject}'


class GateEntryExit(models.Model):
    """Track gate entry and exit events for all personnel."""

    OPERATION_CHOICES = [
        ('entry', 'دخول'),
        ('exit', 'خروج'),
    ]

    person = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='gate_entries', verbose_name='الشخص')
    operation = models.CharField(
        max_length=10, choices=OPERATION_CHOICES, verbose_name='نوع العملية')
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name='الوقت')
    location = models.CharField(max_length=200, default='البوابة الرئيسية', verbose_name='الموقع')
    verified_by_face = models.BooleanField(default=True, verbose_name='تم التحقق بالوجه')
    notes = models.TextField(blank=True, verbose_name='ملاحظات')

    class Meta:
        verbose_name = 'سجل بوابة'
        verbose_name_plural = 'سجلات البوابات'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['person', 'timestamp']),
            models.Index(fields=['operation', 'timestamp']),
        ]

    def __str__(self):
        return f'{self.person.name} - {self.get_operation_display()} - {self.timestamp}'
