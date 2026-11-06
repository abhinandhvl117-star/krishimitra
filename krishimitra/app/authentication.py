from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.authentication import JWTAuthentication

class ActiveAccountJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        result = super().authenticate(request)
        if result is None:
            return None
        user, token = result
        profile = getattr(user, "profile", None)
        if profile is not None and not profile.is_active_account:
            raise AuthenticationFailed("Your account has been disabled.")
        return user, token