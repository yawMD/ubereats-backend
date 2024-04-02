from rest_framework import permissions


class IsAdminUser(permissions.BasePermission):
    """
    Custom permission to only allow admin users to access a view.
    """

    def has_permission(self, request, view):
        # If the user is authenticated, check their profile for the 'admin' role
        if request.user and request.user.is_authenticated:
            return request.user.profile.role == 'admin'
        # If the user is not authenticated, return False
        return False


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow owners and admins to edit or delete, but
    allow any authenticated user to view (GET, HEAD, OPTIONS).
    """

    def has_permission(self, request, view):
        # Allow any authenticated user to view by checking for safe methods
        if request.method in permissions.SAFE_METHODS:
            return True

        # Check if the user is authenticated
        if not request.user or not request.user.is_authenticated:
            return False

        # Allow owners and admins to perform any action
        profile = request.user.profile
        return profile.role in ['admin', 'owner']

    def has_object_permission(self, request, view, obj):
        # Allow any authenticated user to view the object
        if request.method in permissions.SAFE_METHODS:
            return True

        # For other methods, check if the user is an admin or the owner of the object
        return request.user.profile.role == 'admin' or obj.owner == request.user
