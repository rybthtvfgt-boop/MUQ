"""
Monitoring System Models
"""
from django.db import models


class TrainedModel(models.Model):
    """Store information about trained AI models"""
    name = models.CharField(max_length=200)
    version = models.CharField(max_length=50)
    accuracy = models.FloatField()
    model_path = models.CharField(max_length=500)
    training_log_path = models.CharField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'نموذج مدرب'
        verbose_name_plural = 'النماذج المدربة'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} v{self.version} ({self.accuracy}%)'


class TrainingSession(models.Model):
    """Track training sessions"""
    STATUS_CHOICES = [
        ('pending', 'قيد الانتظار'),
        ('running', 'جاري التدريب'),
        ('completed', 'مكتمل'),
        ('failed', 'فشل'),
        ('stopped', 'متوقف'),
    ]

    model = models.ForeignKey(TrainedModel, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    progress = models.IntegerField(default=0)
    current_stage = models.CharField(max_length=200, blank=True)
    error_message = models.TextField(blank=True)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'جلسة تدريب'
        verbose_name_plural = 'جلسات التدريب'
        ordering = ['-started_at']

    def __str__(self):
        return f'Training session {self.id} - {self.get_status_display()}'
