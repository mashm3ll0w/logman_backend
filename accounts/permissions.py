from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsSuperAdmin(BasePermission):
    """Only active superusers are allowed (any method)."""
    message = "Only a super admin can perform this action."

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and user.is_active and user.is_superuser)


class IsSuperAdminOrReadOnly(BasePermission):
    """Read access for any authenticated user; write (create/update/delete) is
    restricted to active super admins. Used so everyone can *view* users but only
    admins can *manage* them."""
    message = "Only a super admin can manage users."

    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated and user.is_active):
            return False
        if request.method in SAFE_METHODS:
            return True
        return user.is_superuser
