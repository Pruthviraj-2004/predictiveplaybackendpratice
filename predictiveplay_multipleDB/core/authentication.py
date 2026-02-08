from rest_framework_simplejwt.authentication import JWTAuthentication

class TokenOnlyJWTAuthentication(JWTAuthentication):
    """
    Custom JWT authentication that:
    - Validates token
    - Does NOT try to fetch a Django user
    """

    def get_user(self, validated_token):
        # 🚫 Disable Django user lookup completely
        return None

from rest_framework_simplejwt.authentication import JWTAuthentication

class CookieJWTAuthentication(JWTAuthentication):
    """
    JWT auth that reads token from HttpOnly cookie instead of header.
    """

    def authenticate(self, request):
        raw_token = request.COOKIES.get("access_token")
        if not raw_token:
            return None

        validated_token = self.get_validated_token(raw_token)

        # ❌ no Django user lookup
        return None, validated_token
