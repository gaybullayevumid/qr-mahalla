from rest_framework.permissions import BasePermission


class HouseAccessPermission(BasePermission):
    """
    Super admin → all houses
    Neighborhood admin → only own neighborhood
    User/Owner → only own house
    """

    def has_object_permission(self, request, view, obj):
        user = request.user

        if not user.is_authenticated or not hasattr(user, 'role'):
            return False

        if user.role == "super_admin":
            return True

        if user.role == "government":
            return True

        if user.role == "mahalla_admin":
            return hasattr(user, "mahalla") and obj.mahalla == user.mahalla

        # Regular users and owners can access their own houses
        if user.role in ["user", "owner"]:
            return obj.owner == user

        return False
