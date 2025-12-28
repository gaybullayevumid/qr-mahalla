from rest_framework.permissions import BasePermission


class HouseAccessPermission(BasePermission):
    """
    Admin → all houses
    Leader (mahalla admin) → only own neighborhood
    Client/Agent → only own house
    """

    def has_object_permission(self, request, view, obj):
        user = request.user

        if not user.is_authenticated or not hasattr(user, 'role'):
            return False

        if user.role == "admin":
            return True

        if user.role == "gov":
            return True

        if user.role == "leader":
            return hasattr(user, "mahalla") and obj.mahalla == user.mahalla

        # Regular clients and agents can access their own houses
        if user.role in ["client", "agent"]:
            return obj.owner == user

        return False
