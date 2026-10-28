"""
Monitoring System URLs
"""
from django.urls import path
from . import views

urlpatterns = [
    path('training/start/', views.start_training, name='start_training'),
    path('training/progress/', views.get_training_progress, name='training_progress'),
    path('training/stop/', views.stop_training, name='stop_training'),
    path('training/reset/', views.reset_training, name='reset_training'),
    path('training/sessions/<int:session_id>/', views.get_training_session, name='training_session'),
    path('dataset/info/', views.get_dataset_info, name='dataset_info'),
    path('dataset/upload/', views.upload_training_image, name='upload_training_image'),
    path('predict/', views.predict_image, name='predict_image'),
]
