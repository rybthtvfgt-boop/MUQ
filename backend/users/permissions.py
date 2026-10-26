from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsSuperAdmin(BasePermission):
    message = 'هذه العملية تتطلب صلاحيات المشرف الأعلى.'

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and user.is_super_admin)


class IsSuperAdminOrReadOnly(BasePermission):
    """Master data (departments, stages, branches, schedules) is readable by any
    signed-in account but writable only by the super admin."""

    message = 'تعديل البيانات الأساسية يتطلب صلاحيات المشرف الأعلى.'

    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated):
            return False
        if request.method in SAFE_METHODS:
            return True
        return user.is_super_admin


class IsSelfOrCreate(BasePermission):
    """Ordinary accounts may read and update themselves; only a super admin may write others or delete."""

    message = 'لا تملك صلاحية الوصول إلى هذا السجل.'

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        # Super admin can do anything
        if request.user.is_super_admin:
            return True
        
        # Users can read their own data
        if request.method in SAFE_METHODS:
            return obj == request.user
        
        # Users can update their own account (but not delete)
        if request.method in ['PUT', 'PATCH']:
            return obj == request.user
        
        # Users cannot delete their own account
        return False


class IsRegistrationStaff(BasePermission):
    """Registration staff can read users (for face registration) but cannot modify user data."""

    message = 'هذه العملية تتطلب صلاحيات قسم التسجيل.'

    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated):
            return False
        # Only registration staff or super admin
        return user.is_super_admin or user.user_type == user.UserType.REGISTRATION

    def has_object_permission(self, request, view, obj):
        # Super admin can do anything
        if self.request.user.is_super_admin:
            return True
        
        # Registration staff can only read users (for face registration)
        if request.method in SAFE_METHODS:
            return True
        
        # Cannot modify user data
        return False
