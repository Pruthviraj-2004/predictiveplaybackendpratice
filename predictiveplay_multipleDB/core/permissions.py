from rest_framework.permissions import BasePermission

class HasValidJWT(BasePermission):
    """
    Allows access if a valid JWT is present.
    Does NOT depend on request.user.
    """

    def has_permission(self, request, view):
        return request.auth is not None
