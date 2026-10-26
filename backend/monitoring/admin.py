"""
Monitoring System Admin
"""
from django.contrib import admin
from .models import TrainedModel, TrainingSession


@admin.register(TrainedModel)
class TrainedModelAdmin(admin.ModelAdmin):
    list_display = ['name', 'version', 'accuracy', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'version']


@admin.register(TrainingSession)
class TrainingSessionAdmin(admin.ModelAdmin):
    list_display = ['id', 'model', 'status', 'progress', 'started_at', 'completed_at']
    list_filter = ['status', 'started_at']
    search_fields = ['current_stage', 'error_message']
    readonly_fields = ['started_at', 'completed_at']
