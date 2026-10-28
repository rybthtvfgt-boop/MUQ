from django.contrib import admin
from .models import Attendance, Schedule, GateEntryExit

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['person', 'date', 'time', 'status', 'location']
    list_filter = ['status', 'date', 'location']
    search_fields = ['person__name']

@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ['day', 'time', 'subject', 'teacher', 'department']
    list_filter = ['day', 'department']
    search_fields = ['subject', 'teacher__name']

@admin.register(GateEntryExit)
class GateEntryExitAdmin(admin.ModelAdmin):
    list_display = ['person', 'operation', 'timestamp', 'location', 'verified_by_face']
    list_filter = ['operation', 'verified_by_face', 'timestamp', 'location']
    search_fields = ['person__name']
    readonly_fields = ['timestamp']
