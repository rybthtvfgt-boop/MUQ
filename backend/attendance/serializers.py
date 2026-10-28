from rest_framework import serializers
from .models import Attendance, Schedule, GateEntryExit

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

class GateEntryExitSerializer(serializers.ModelSerializer):
    person_name = serializers.CharField(source='person.name', read_only=True)
    person_type = serializers.CharField(source='person.user_type', read_only=True)
    person_code = serializers.CharField(source='person.code', read_only=True)

    class Meta:
        model = GateEntryExit
        fields = '__all__'
        read_only_fields = ['person', 'timestamp', 'verified_by_face']
