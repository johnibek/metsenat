from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.exceptions import ValidationError

from shared.utils import token



class SignUpStaffUserSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    username = serializers.CharField(required=True, max_length=128)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, max_length=128, write_only=True)
    confirm_password = serializers.CharField(required=True, max_length=128, write_only=True)

    def validate(self, attrs):
        password = attrs.get('password')
        confirm_password = attrs.get('confirm_password')
        username = attrs.get('username')

        if password != confirm_password:
            raise ValidationError(
                {
                    'message': 'Your password does not match.'
                }
            )

        if password:
            validate_password(password)

        if len(username) < 5 or len(username) > 30:
            raise ValidationError(
                {
                    'message': 'Your username must be 5 and 30 characters long'
                }
            )

        if username.isdigit():
            raise ValidationError(
                {
                    'message': 'Your username is entirely numeric'
                }
            )

        return attrs


    def create(self, validated_data):
        new_staff_user = User(
            username=validated_data['username'],
            email=validated_data['email'],
            is_staff=True
        )
        new_staff_user.set_password(validated_data['password'])
        new_staff_user.save()
        return new_staff_user


    def to_representation(self, instance):
        data = super(SignUpStaffUserSerializer, self).to_representation(instance)
        tokens = token(instance)
        data.update(tokens)
        return data



class LogoutStaffUserSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()


class ViewStaffUserDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ['password', 'groups', 'user_permissions']


class ChangeStaffUserDataSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email']


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_new_password = serializers.CharField(required=True)

    def validate(self, attrs):
        new_password = attrs.get('new_password')
        confirm_new_password = attrs.get('confirm_new_password')
        if new_password != confirm_new_password:
            raise ValidationError(
                {
                    'success': False,
                    'message': 'Your new password does not match.'
                }
            )
        if new_password:
            validate_password(new_password)

        return attrs
