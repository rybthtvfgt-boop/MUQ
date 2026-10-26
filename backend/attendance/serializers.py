from rest_framework import serializers
from .models import Attendance, Schedule

class AttendanceSerializer(serializers.ModelSerializer):
    person_name = serializers.CharField(source='person.name', read_only=True)
    person_type = serializers.CharField(source='person.user_type', read_only=True)

    class Meta:
        model = Attendance
        fields = '__all__'
        read_only_fields = ['person', 'recorded_by', 'date', 'time', 'created_at']

class ScheduleSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source='teacher.name', read_only=True)

    class Meta:
        model = Schedule
        fields = '__all__'
