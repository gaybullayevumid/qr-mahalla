from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and hasattr(request.user, "role")
            and request.user.role == "admin"
        )


class IsLeader(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and hasattr(request.user, "role")
            and request.user.role == "leader"
        )


class IsAdminOrGov(BasePermission):
    """
    Permission class that allows access to admin, leader, and government users.

    Only users with 'admin', 'leader', or 'gov' roles can access.
    """

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and hasattr(request.user, "role")
            and request.user.role in ["admin", "leader", "gov"]
        )
