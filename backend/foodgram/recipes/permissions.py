from rest_framework import permissions


class IsAuthorOrAdminOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.method == 'POST':
            return request.user.is_authenticated

        if request.query_params.get('tags'):
            return request.user.is_authenticated

        return True

    def has_object_permission(self, request, view, obj):

        if request.method in permissions.SAFE_METHODS:
            return True

        return request.user.is_authenticated and (
            request.user == obj.author
            or request.user.is_superuser
        )
