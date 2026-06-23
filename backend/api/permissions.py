from rest_framework.permissions import BasePermission


class IsAdminAuthenticated(BasePermission):
    def has_permission(self, request, view):
        return 'user_id' in request.session
