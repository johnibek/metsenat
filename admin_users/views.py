from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from shared.permissions import IsStaffUser, IsSuperUser
from .serializers import (SignUpStaffUserSerializer, LogoutStaffUserSerializer, ChangeStaffUserDataSerializer,
                          ViewStaffUserDataSerializer, ChangePasswordSerializer)


@extend_schema(
        request=SignUpStaffUserSerializer,
        tags=['staff users authentication'],
        description="""
        Sign up staff users. Only superusers can do this action.
        """
    )
class SignUpStaffUserAPIView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated, IsSuperUser]  # Only superusers can create new staff users.
    serializer_class = SignUpStaffUserSerializer


@extend_schema(
        request=LogoutStaffUserSerializer,
        tags=['staff users authentication']
)
class LogoutStaffUserAPIView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated, IsStaffUser]
    serializer_class = LogoutStaffUserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            refresh_token = serializer.validated_data.get('refresh_token')
            refresh = RefreshToken(refresh_token)
            refresh.blacklist()
            return Response(
                {
                    'success': True,
                    'message': 'You have successfully logged out'
                }, status=status.HTTP_200_OK
            )
        except TokenError:
            return Response(
                {
                    'success': False,
                    'message': 'Token is incorrect or expired.'
                }, status=status.HTTP_400_BAD_REQUEST
            )


@extend_schema(
        request=ViewStaffUserDataSerializer,
        tags=['staff users authentication'],
        description="""
        Profile data. You can only see your own data.
        """
    )
class ViewStaffUserDataAPIView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated, IsStaffUser]
    serializer_class = ViewStaffUserDataSerializer

    def get_object(self):
        return self.request.user


@extend_schema(
        request=ChangeStaffUserDataSerializer,
        tags=['staff users authentication'],
        description="""
        Update profile data. You can only update your first name, last name, email
        """
    )
class ChangeStaffUserDataAPIView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated, IsStaffUser]
    serializer_class = ChangeStaffUserDataSerializer
    http_method_names = ['patch', 'put']

    def get_object(self):
        return self.request.user


@extend_schema(
        request=ChangePasswordSerializer,
        tags=['staff users authentication'],
        description="""
        Change staff user password.
        """
    )
class ChangePasswordAPIView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated, IsStaffUser]
    serializer_class = ChangePasswordSerializer
    http_method_names = ['put']

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        old_password = serializer.validated_data.get('old_password')
        new_password = serializer.validated_data.get('new_password')

        if not user.check_password(old_password):
            return Response(
                {"error": "Your old password is incorrect."}, status=status.HTTP_400_BAD_REQUEST
            )

        user.set_password(new_password)
        user.save()
        return Response(
            {
                "success": True,
                "message": "Password changed successfully."
            }, status=status.HTTP_200_OK
        )


@extend_schema_view(
        post=extend_schema(tags=['staff users authentication']),
    )
class LoginStaffUserView(TokenObtainPairView):
    pass


@extend_schema_view(
        post=extend_schema(tags=['staff users authentication']),
    )
class LoginRefreshView(TokenRefreshView):
    pass