from rest_framework.permissions import BasePermission

class IsVerifiedGovernment(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role == 'government' and
            request.user.is_verified
        )
