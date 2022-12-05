from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    """Кастомное разрешение,
    только автор имеет право на редактирование."""
    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
            or request.user.is_admin or request.user.is_moderator
        )


class AdminOrReadOnly(permissions.BasePermission):
    """Permission to CRUD genres, category, titles in database"""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return (request.user.is_authenticated
                and request.user.is_admin)

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_admin)


class IsSuperUserOrAdminPermission(permissions.BasePermission):
    """Allow make requests for superuser or admin only."""
    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        return request.user.is_superuser or request.user.is_admin
