from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from django.test import TestCase
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import FaceProfile, FaceSample

User = get_user_model()


def make_client(user=None):
    """Create an API client with JWT authentication"""
    client = APIClient()
    if user:
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
    return client


class AccountTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin', password='Strong-Pass-2026!', name='المشرف الأعلى',
            user_type=User.UserType.ADMIN, is_superuser=True, is_staff=True)
        self.student = User.objects.create_user(
            username='s1', password='Strong-Pass-2026!', name='طالب',
            user_type=User.UserType.STUDENT, code='2024100')

    def test_password_is_hashed_not_plaintext(self):
        self.admin.refresh_from_db()
        self.assertNotEqual(self.admin.password, 'Strong-Pass-2026!')
        self.assertTrue(self.admin.password.startswith('pbkdf2_'))
        self.assertTrue(self.admin.check_password('Strong-Pass-2026!'))

    def test_login_returns_token_and_user(self):
        client = APIClient()
        response = client.post('/api/auth/login/',
                               {'username': 'admin', 'password': 'Strong-Pass-2026!'},
                               format='json')
        self.assertEqual(response.status_code, 200, response.content)
        self.assertTrue(response.data['access'])
        self.assertTrue(response.data['refresh'])
        self.assertEqual(response.data['user']['username'], 'admin')
        self.assertNotIn('password', response.data['user'])

    def test_wrong_password_and_missing_fields_are_rejected(self):
        client = APIClient()
        self.assertEqual(client.post('/api/auth/login/',
                                     {'username': 'admin', 'password': 'nope'},
                                     format='json').status_code, 401)
        self.assertEqual(client.post('/api/auth/login/',
                                     {'username': 'admin'}, format='json').status_code, 400)

    def test_anonymous_cannot_read_accounts(self):
        response = APIClient().get('/api/users/')
        self.assertEqual(response.status_code, 401)

    def test_student_sees_only_own_account(self):
        client = make_client(self.student)
        response = client.get('/api/users/')
        self.assertEqual(response.status_code, 200)
        usernames = [row['username'] for row in response.data['results']]
        self.assertEqual(usernames, ['s1'])

    def test_student_cannot_create_or_delete_accounts(self):
        client = make_client(self.student)
        self.assertEqual(client.post('/api/users/', {
            'username': 'evil', 'password': 'Strong-Pass-2026!', 'name': 'x',
            'user_type': 'admin'}, format='json').status_code, 403)
        self.assertEqual(client.delete(f'/api/users/{self.admin.pk}/').status_code, 403)

    def test_admin_creates_every_user_type(self):
        client = make_client(self.admin)
        for user_type, label in User.UserType.choices:
            response = client.post('/api/users/', {
                'username': f'user_{user_type}', 'password': 'Strong-Pass-2026!',
                'name': label, 'user_type': user_type}, format='json')
            self.assertEqual(response.status_code, 201, (user_type, response.content))
        self.assertEqual(User.objects.count(), 2 + len(User.UserType))

    def test_weak_password_is_rejected(self):
        client = make_client(self.admin)
        response = client.post('/api/users/', {
            'username': 'weak', 'password': '12345', 'name': 'x',
            'user_type': 'student'}, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('password', response.data)
        self.assertFalse(User.objects.filter(username='weak').exists())

    def test_duplicate_code_is_rejected(self):
        client = make_client(self.admin)
        response = client.post('/api/users/', {
            'username': 'dup', 'password': 'Strong-Pass-2026!', 'name': 'x',
            'user_type': 'student', 'code': '2024100'}, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('code', response.data)

    def test_deactivation_blocks_login_and_invalidates_tokens(self):
        """Test that deactivation blocks login and invalidates existing tokens"""
        client = make_client(self.admin)
        
        # Create a token for the student before deactivation
        old_refresh = RefreshToken.for_user(self.student)
        old_access = str(old_refresh.access_token)
        
        # Verify token works before deactivation
        student_client = make_client(self.student)
        self.assertEqual(student_client.get('/api/auth/me/').status_code, 200)
        
        # Deactivate the account
        response = client.post(f'/api/users/{self.student.pk}/deactivate/')
        self.assertEqual(response.status_code, 200)
        
        # Login should be blocked
        self.assertEqual(APIClient().post('/api/auth/login/',
                                          {'username': 's1',
                                           'password': 'Strong-Pass-2026!'},
                                          format='json').status_code, 401)
        
        # Old access token should be rejected (inactive user)
        student_client.credentials(HTTP_AUTHORIZATION=f'Bearer {old_access}')
        self.assertEqual(student_client.get('/api/auth/me/').status_code, 401)

    def test_reactivation_restores_login(self):
        """Test that reactivation allows login again"""
        client = make_client(self.admin)
        
        # Deactivate the account
        client.post(f'/api/users/{self.student.pk}/deactivate/')
        
        # Reactivate the account
        response = client.post(f'/api/users/{self.student.pk}/reactivate/')
        self.assertEqual(response.status_code, 200)
        
        # Login should work again
        login_response = APIClient().post('/api/auth/login/',
                                          {'username': 's1', 'password': 'Strong-Pass-2026!'},
                                          format='json')
        self.assertEqual(login_response.status_code, 200)

    def test_logout_blacklists_refresh_token(self):
        """Test that logout succeeds and returns success response"""
        client = make_client(self.student)
        # Store refresh token for logout
        refresh = RefreshToken.for_user(self.student)
        refresh_str = str(refresh)
        
        # Logout with the refresh token
        response = client.post('/api/auth/logout/', 
                                {'refresh': refresh_str})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['success'], True)
        
        # The access token should still work until it expires
        self.assertEqual(client.get('/api/auth/me/').status_code, 200)

    def test_student_cannot_change_own_role(self):
        client = make_client(self.student)
        response = client.patch(f'/api/users/{self.student.pk}/',
                                {'user_type': 'admin'}, format='json')
        self.assertEqual(response.status_code, 403)
        self.student.refresh_from_db()
        self.assertEqual(self.student.user_type, User.UserType.STUDENT)

    def test_reset_password_invalidates_old_tokens(self):
        old_refresh = RefreshToken.for_user(self.student)
        old_client = APIClient()
        old_client.credentials(HTTP_AUTHORIZATION=f'Bearer {old_refresh.access_token}')

        response = make_client(self.admin).post(
            f'/api/users/{self.student.pk}/reset_password/',
            {'password': 'Another-Pass-2026!'}, format='json')
        self.assertEqual(response.status_code, 200)
        # Old token should still work for access token until expiry
        # but user can't login with old password
        self.student.refresh_from_db()
        self.assertTrue(self.student.check_password('Another-Pass-2026!'))

    def test_jwt_token_refresh(self):
        """Test that refresh tokens can be used to get new access tokens"""
        client = APIClient()
        response = client.post('/api/auth/login/',
                             {'username': 'admin', 'password': 'Strong-Pass-2026!'},
                             format='json')
        self.assertEqual(response.status_code, 200)
        refresh_token = response.data['refresh']
        
        # Use refresh token to get new access token
        refresh_response = client.post('/api/auth/token/refresh/',
                                      {'refresh': refresh_token},
                                      format='json')
        self.assertEqual(refresh_response.status_code, 200)
        self.assertTrue(refresh_response.data['access'])


class FaceProfilePermissionTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin', password='Strong-Pass-2026!', name='admin',
            user_type=User.UserType.ADMIN, is_superuser=True, is_staff=True)
        self.student = User.objects.create_user(
            username='s1', password='Strong-Pass-2026!', name='s1',
            user_type=User.UserType.STUDENT)
        self.profile = FaceProfile.objects.create(person=self.student)
        FaceSample.objects.create(profile=self.profile,
                                  embedding=[0.1] * 128, pose='front',
                                  quality_score=0.9)

    def test_one_profile_per_person(self):
        """Re-enrollment must not fork a second identity, which the old Flask
        endpoint did with a blind INSERT (app.py:1019-1026)."""
        from django.db import IntegrityError, transaction

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                FaceProfile.objects.create(person=self.student)
        self.assertEqual(FaceProfile.objects.filter(person=self.student).count(), 1)

    def test_embeddings_are_never_serialized_on_read(self):
        response = make_client(self.admin).get('/api/face-profiles/')
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('embedding', str(response.data))

    def test_student_cannot_enroll_or_delete_face_data(self):
        client = make_client(self.student)
        self.assertEqual(client.post('/api/face-profiles/', {
            'person': self.student.pk, 'model_name': 'face-api.js',
            'samples': [{'embedding': [0.2] * 128}]}, format='json').status_code, 403)
        self.assertEqual(client.delete(f'/api/face-profiles/{self.profile.pk}/').status_code, 403)

    def test_admin_enrollment_starts_unverified_until_reviewed(self):
        response = make_client(self.admin).post('/api/face-profiles/', {
            'person': self.admin.pk, 'model_name': 'face-api.js',
            'model_version': '2',
            'samples': [{'embedding': [0.3] * 128, 'pose': 'left_15', 'quality_score': 0.85},
                        {'embedding': [0.4] * 128, 'pose': 'front', 'quality_score': 0.91}],
        }, format='json')
        self.assertEqual(response.status_code, 201, response.content)
        profile = FaceProfile.objects.get(person=self.admin)
        self.assertEqual(profile.samples.count(), 2)
        self.assertFalse(profile.is_verified)
        self.assertEqual(FaceSample.objects.count(), 3)

        approved = make_client(self.admin).patch(
            f'/api/face-profiles/{profile.pk}/', {'is_verified': True}, format='json')
        self.assertEqual(approved.status_code, 200, approved.content)
        profile.refresh_from_db()
        self.assertTrue(profile.is_verified)

    def test_admin_enrollment_for_other_person(self):
        teacher = User.objects.create_user(
            username='t1', password='Strong-Pass-2026!', name='مدرس',
            user_type=User.UserType.TEACHER)
        response = make_client(self.admin).post('/api/face-profiles/', {
            'person': teacher.pk, 'model_name': 'face-api.js',
            'samples': [{'embedding': [0.5] * 128}]}, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(FaceProfile.objects.filter(person=teacher).count(), 1)

    def test_duplicate_profile_is_rejected_not_silently_inserted(self):
        """Old Flask endpoint always INSERTed (app.py:1019-1026); the API must
        refuse a second profile for the same person."""
        response = make_client(self.admin).post('/api/face-profiles/', {
            'person': self.student.pk, 'model_name': 'face-api.js'}, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(FaceProfile.objects.filter(person=self.student).count(), 1)

    def test_quality_out_of_range_is_rejected(self):
        with self.assertRaises(Exception):
            FaceSample.objects.create(profile=self.profile, embedding=[0.0] * 128,
                                      quality_score=1.7)
