from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    FaceProfileViewSet, UserViewSet, login_view, logout_view, me_view,
    login_template_view, logout_template_view,
    admin_dashboard, teacher_dashboard, student_dashboard, staff_dashboard,
    recognize_face, verify_face
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'face-profiles', FaceProfileViewSet, basename='face-profile')

urlpatterns = [
    # API endpoints
    path('auth/login/', login_view, name='api-login'),
    path('auth/logout/', logout_view, name='api-logout'),
    path('auth/me/', me_view, name='api-me'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Face recognition endpoints
    path('face-recognition/recognize/', recognize_face, name='recognize-face'),
    path('face-recognition/verify/', verify_face, name='verify-face'),
    
    path('', include(router.urls)),
]

# Template views will be added in main urls.py
