from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Доступ на чтение всем
    """

    def has_permission(self, request, view):
        return bool(request.method in permissions.SAFE_METHODS
                    or
                    request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return bool(request.user and request.user.is_staff
                    or
                    request.user and obj.author == request.user)


class IsAuthorOrAuthReadOnly(permissions.BasePermission):
    """
    Доступ на чтение авторизованным
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return bool(request.user and request.user.is_authenticated)

        return bool(request.user and request.user.is_staff
                    or
                    request.user and obj.author == request.user)
