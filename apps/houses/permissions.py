from rest_framework.permissions import BasePermission


class HouseAccessPermission(BasePermission):
    """Permission class for house access control.

    Access rules by role:
        - Admin: Access to all houses
        - Government: Access to all houses
        - Leader (mahalla admin): Access to houses in their neighborhood only
        - Client/Agent: Access to their own houses only
    """

    def has_object_permission(self, request, view, obj):
        user = request.user

        if not user.is_authenticated or not hasattr(user, "role"):
            return False

        if user.role == "admin":
            return True

        if user.role == "gov":
            return True

        if user.role == "leader":
            return hasattr(user, "mahalla") and obj.mahalla == user.mahalla

        if user.role in ["client", "agent"]:
            return obj.owner == user

        return False
