from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.shortcuts import render, redirect
from rest_framework import status, viewsets, throttling
from rest_framework.decorators import action, api_view, permission_classes, throttle_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import FaceProfile, User
from .permissions import IsSelfOrCreate, IsSuperAdmin, IsRegistrationStaff
from .serializers import FaceProfileSerializer, UserSerializer


class LoginRateThrottle(throttling.AnonRateThrottle):
    """Custom throttle for login endpoint - 5 attempts per minute"""
    rate = '5/minute'
    scope = 'login'


class UserViewSet(viewsets.ModelViewSet):
    """Accounts. Writes require the super admin; users can update their own account.
    Registration staff can read users for face registration purposes."""

    serializer_class = UserSerializer
    permission_classes = [IsSelfOrCreate]

    def get_queryset(self):
        user = self.request.user
        if user.is_super_admin:
            return User.objects.select_related('department', 'stage', 'branch').all()
        # Registration staff can read all users for face registration
        if user.user_type == user.UserType.REGISTRATION:
            return User.objects.select_related('department', 'stage', 'branch').all()
        return User.objects.filter(pk=user.pk)

    def create(self, request, *args, **kwargs):
        if not request.user.is_super_admin:
            return Response({'error': 'إنشاء الحسابات يتطلب صلاحيات المشرف الأعلى.'},
                            status=status.HTTP_403_FORBIDDEN)
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """Allow users to update their own account, but prevent changing sensitive fields"""
        instance = self.get_object()
        if not request.user.is_super_admin:
            # Prevent changing sensitive fields
            if 'user_type' in request.data or 'is_superuser' in request.data or 'is_staff' in request.data:
                return Response(
                    {'error': 'تغيير الصفة الوظيفية أو الصلاحيات يتطلب المشرف الأعلى.'},
                    status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        if not request.user.is_super_admin:
            return Response({'error': 'حذف الحسابات يتطلب صلاحيات المشرف الأعلى.'},
                            status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=['post'], permission_classes=[IsSuperAdmin])
    def deactivate(self, request, pk=None):
        """Deactivation keeps the account, its history and the audit trail.
        Also invalidates all JWT tokens for this user."""
        from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken
        from rest_framework_simplejwt.tokens import RefreshToken, OutstandingToken
        
        user = self.get_object()
        user.is_active = False
        user.save(update_fields=['is_active', 'updated_at'])
        
        # Blacklist all outstanding refresh tokens for this user
        try:
            for token in OutstandingToken.objects.filter(user_id=user.id):
                try:
                    refresh_token = RefreshToken(token.token)
                    refresh_token.blacklist()
                except Exception:
                    # Token might already be invalid or blacklisted
                    pass
        except Exception:
            # If token blacklist table doesn't exist or other error, continue
            pass
        
        return Response({'status': 'deactivated', 'id': user.pk})

    @action(detail=True, methods=['post'], permission_classes=[IsSuperAdmin])
    def reactivate(self, request, pk=None):
        user = self.get_object()
        user.is_active = True
        user.save(update_fields=['is_active', 'updated_at'])
        return Response({'status': 'reactivated', 'id': user.pk})

    @action(detail=True, methods=['post'], permission_classes=[IsSuperAdmin])
    def reset_password(self, request, pk=None):
        from django.contrib.auth.password_validation import validate_password
        from django.core.exceptions import ValidationError as DjangoValidationError
        
        user = self.get_object()
        new_password = request.data.get('password')
        if not new_password:
            return Response({'error': 'كلمة المرور الجديدة مطلوبة.'},
                            status=status.HTTP_400_BAD_REQUEST)
        
        # Validate password strength
        try:
            validate_password(new_password, user)
        except DjangoValidationError as e:
            return Response({'error': '; '.join(e.messages)},
                            status=status.HTTP_400_BAD_REQUEST)
        
        user.set_password(new_password)
        user.save(update_fields=['password'])
        return Response({'status': 'password_reset', 'id': user.pk})


class FaceProfileViewSet(viewsets.ModelViewSet):
    """Biometric profiles. Enrollment/verification is a super-admin action.
    Registration staff can create face profiles for users."""

    serializer_class = FaceProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = FaceProfile.objects.select_related('person').prefetch_related('samples')
        if self.request.user.is_super_admin:
            return qs
        if self.request.user.user_type == self.request.user.UserType.REGISTRATION:
            return qs
        return qs.filter(person=self.request.user)

    def create(self, request, *args, **kwargs):
        """Allow registration staff to create face profiles"""
        if not request.user.is_super_admin and request.user.user_type != request.user.UserType.REGISTRATION:
            return Response({'error': 'إنشاء ملفات الوجه يتطلب صلاحيات المشرف الأعلى أو قسم التسجيل.'},
                            status=status.HTTP_403_FORBIDDEN)
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        if not request.user.is_super_admin:
            return Response({'error': 'تعديل ملفات الوجه يتطلب صلاحيات المشرف الأعلى.'},
                            status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        if not request.user.is_super_admin:
            return Response({'error': 'حذف ملفات الوجه يتطلب صلاحيات المشرف الأعلى.'},
                            status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)


@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([LoginRateThrottle])
def login_view(request):
    """JWT login. Replaces the plaintext localStorage check in Js/login.js."""
    username = (request.data.get('username') or '').strip()
    password = request.data.get('password') or ''

    if not username or not password:
        return Response({'error': 'اسم المستخدم وكلمة المرور مطلوبان.'},
                        status=status.HTTP_400_BAD_REQUEST)

    # authenticate() rejects inactive accounts, so a deactivated person cannot
    # obtain a token even with the correct password.
    user = authenticate(request, username=username, password=password)
    if user is None:
        return Response({'error': 'بيانات الدخول غير صحيحة.'},
                        status=status.HTTP_401_UNAUTHORIZED)

    refresh = RefreshToken.for_user(user)
    return Response({
        'success': True,
        'access': str(refresh.access_token),
        'refresh': str(refresh),
        'user': {
            'id': user.id,
            'username': user.username,
            'name': user.name,
            'user_type': user.user_type,
            'email': user.email,
        },
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def logout_view(request):
    """Logout and blacklist refresh token"""
    from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
    import logging
    
    logger = logging.getLogger(__name__)
    refresh_token = request.data.get('refresh')
    
    if not refresh_token:
        # No token provided, but logout still succeeds on client side
        return Response({'success': True, 'message': 'No refresh token provided'})
    
    try:
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({'success': True, 'message': 'Token blacklisted successfully'})
    except (InvalidToken, TokenError) as e:
        # Token was already invalid or expired - this is okay
        logger.warning(f'Logout attempted with invalid token: {str(e)}')
        return Response({'success': True, 'message': 'Token was already invalid'})
    except Exception as e:
        # Log other errors without exposing sensitive information
        logger.error(f'Unexpected error during logout: {str(e)}')
        return Response(
            {'success': False, 'message': 'Logout encountered an error, but you have been logged out client-side'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me_view(request):
    return Response(UserSerializer(request.user).data)


# ============ Django Template Views ============

def login_template_view(request):
    """Render login page"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)
            # Redirect based on user type
            if user.user_type == 'admin':
                return redirect('admin_dashboard')
            elif user.user_type == 'teacher':
                return redirect('teacher_dashboard')
            elif user.user_type == 'student':
                return redirect('student_dashboard')
            elif user.user_type in ['administrative', 'security', 'service']:
                return redirect('staff_dashboard')
            elif user.user_type == 'gate':
                return redirect('gate_dashboard')
            elif user.user_type == 'registration':
                return redirect('registration_dashboard')
        else:
            return render(request, 'login.html', {'error': 'بيانات الدخول غير صحيحة'})

    return render(request, 'login.html')


def logout_template_view(request):
    """Logout and redirect to login"""
    auth_logout(request)
    return redirect('login')


def admin_dashboard(request):
    """Admin dashboard view"""
    if not request.user.is_authenticated or not request.user.is_super_admin:
        return redirect('login')

    from departments.models import Department, Stage, Branch
    from attendance.models import Attendance

    context = {
        'user': request.user,
        'students': User.objects.filter(user_type='student').count(),
        'teachers': User.objects.filter(user_type='teacher').count(),
        'staff': User.objects.filter(user_type__in=['administrative', 'security', 'service']).count(),
        'departments': Department.objects.count(),
        'stages': Stage.objects.count(),
        'branches': Branch.objects.count(),
    }
    return render(request, 'admin_dashboard.html', context)


def teacher_dashboard(request):
    """Teacher dashboard view"""
    if not request.user.is_authenticated or request.user.user_type != 'teacher':
        return redirect('login')

    context = {
        'user': request.user,
    }
    return render(request, 'teacher_dashboard.html', context)


def student_dashboard(request):
    """Student dashboard view"""
    if not request.user.is_authenticated or request.user.user_type != 'student':
        return redirect('login')

    context = {
        'user': request.user,
    }
    return render(request, 'student_dashboard.html', context)


def staff_dashboard(request):
    """Staff dashboard view"""
    if not request.user.is_authenticated or request.user.user_type not in ['administrative', 'security', 'service']:
        return redirect('login')

    context = {
        'user': request.user,
    }
    return render(request, 'staff_dashboard.html', context)


# ============ Face Recognition API Views ============

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def recognize_face(request):
    """1:N face recognition endpoint"""
    from .models import FaceSample
    import numpy as np
    
    embedding = request.data.get('embedding')
    if not embedding:
        return Response({'error': 'Embedding required'}, status=400)
    
    if len(embedding) != 128:
        return Response({'error': 'Embedding must be 128-dimensional'}, status=400)
    
    # Simple distance-based matching (placeholder)
    # In production, use actual face recognition library
    best_match = None
    best_distance = float('inf')
    
    samples = FaceSample.objects.select_related('profile__person').all()
    for sample in samples:
        sample_embedding = sample.embedding
        if sample_embedding and len(sample_embedding) == 128:
            # Calculate Euclidean distance
            distance = np.sqrt(sum((a - b) ** 2 for a, b in zip(embedding, sample_embedding)))
            if distance < best_distance:
                best_distance = distance
                best_match = sample
    
    threshold = 0.6
    if best_match and best_distance < threshold:
        person = best_match.profile.person
        return Response({
            'success': True,
            'matched': True,
            'person': {
                'id': person.id,
                'name': person.name,
                'user_type': person.user_type
            },
            'distance': round(best_distance, 4),
            'confidence': max(0, 1 - (best_distance / threshold))
        })
    
    return Response({
        'success': True,
        'matched': False,
        'reason': 'No match found'
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_face(request):
    """1:1 face verification endpoint"""
    from .models import FaceSample
    import numpy as np
    
    person_id = request.data.get('person')
    embedding = request.data.get('embedding')
    
    if not person_id or not embedding:
        return Response({'error': 'Person ID and embedding required'}, status=400)
    
    try:
        person = User.objects.get(pk=person_id)
    except User.DoesNotExist:
        return Response({'error': 'Person not found'}, status=404)
    
    # Get person's face samples
    samples = FaceSample.objects.filter(profile__person=person)
    if not samples.exists():
        return Response({'error': 'No face profile found for this person'}, status=404)
    
    # Calculate best distance
    best_distance = float('inf')
    for sample in samples:
        sample_embedding = sample.embedding
        if sample_embedding and len(sample_embedding) == 128:
            distance = np.sqrt(sum((a - b) ** 2 for a, b in zip(embedding, sample_embedding)))
            if distance < best_distance:
                best_distance = distance
    
    threshold = 0.6
    verified = best_distance < threshold
    
    return Response({
        'success': True,
        'verified': verified,
        'distance': round(best_distance, 4) if best_distance != float('inf') else None,
        'threshold': threshold
    })
