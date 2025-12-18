from rest_framework.permissions import BasePermission


class HouseAccessPermission(BasePermission):
    """
    Super admin → hammasi
    Mahalla admin → faqat o‘z mahallasi
    Owner → faqat o‘z uyi
    """

    def has_object_permission(self, request, view, obj):
        user = request.user

        if not user.is_authenticated or not hasattr(user, 'role'):
            return False

        if user.role == "super_admin":
            return True

        if user.role == "mahalla_admin":
            return hasattr(user, "mahalla") and obj.mahalla == user.mahalla

        if user.role == "owner":
            return obj.owner == user

        return False
