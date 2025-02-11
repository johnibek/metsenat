from rest_framework_simplejwt.tokens import RefreshToken


def token(user):
    refresh_obj = RefreshToken.for_user(user)
    return {
        "access_token": str(refresh_obj.access_token),
        "refresh_token": str(refresh_obj)
    }
