from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .permissions import IsSuperUser
from .serializers import (SignUpStaffUserSerializer, LogoutStaffUserSerializer, ChangeStaffUserDataSerializer,
                          ViewStaffUserDataSerializer, ChangePasswordSerializer)



class SignUpStaffUserAPIView(APIView):
    permission_classes = [IsAuthenticated, IsSuperUser]  # Only superusers can create new staff users.

    @extend_schema(
        request=SignUpStaffUserSerializer,
        tags=['staff users authentication']
    )
    def post(self, request):
        serializer = SignUpStaffUserSerializer(data=request.data, many=False)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class LogoutStaffUserAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=LogoutStaffUserSerializer,
        tags=['staff users authentication']
    )
    def post(self, request):
        serializer = LogoutStaffUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            refresh = serializer.validated_data.get('refresh_token')
            refresh_token = RefreshToken(refresh)
            refresh_token.blacklist()
            return Response(
                {
                    "success": True,
                    "message": 'You have successfully logged out.'
                },
                status=status.HTTP_200_OK
            )

        except TokenError:
            return Response({"message": "Token is incorrect or expired."}, status=status.HTTP_400_BAD_REQUEST)


class ViewStaffUserDataAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=ViewStaffUserDataSerializer,
        tags=['staff users authentication']
    )
    def get(self, request):
        serializer = ViewStaffUserDataSerializer(instance=request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ChangeStaffUserDataAPIView(APIView):
    permission_classes = [IsAuthenticated]
    http_method_names = ['patch', 'put']

    @extend_schema(
        request=ChangeStaffUserDataSerializer,
        tags=['staff users authentication']
    )
    def put(self, request):
        serializer = ChangeStaffUserDataSerializer(instance=request.user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"success": True, "message": "Successfully changed user data."}, status=status.HTTP_200_OK)

    @extend_schema(
        request=ChangeStaffUserDataSerializer,
        tags=['staff users authentication']
    )
    def patch(self, request):
        serializer = ChangeStaffUserDataSerializer(instance=request.user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"success": True, "message": "Successfully changed user data."}, status=status.HTTP_200_OK)


class ChangePasswordAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=ChangePasswordSerializer,
        tags=['staff users authentication']
    )
    def put(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        old_password = serializer.validated_data['old_password']
        new_password = serializer.validated_data['new_password']
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