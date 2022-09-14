from rest_framework.permissions import BasePermission


class IsAnonymous(BasePermission):
    """Доступ только неавторизованным пользователям"""

    def has_permission(self, request, view):
        return f'{request.user}' == 'AnonymousUser'
