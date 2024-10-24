from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.models import Permission
from .models import OperatorPermission

CustomUser = get_user_model()

class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ["id", "name", "codename"]

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            "id", "email", "first_name", "last_name", "phone_number", "role",
            "is_active", "language", "date_joined", "email_verified",
            "profile_complete", "approval_status", "supplier_qr"
        ]
        read_only_fields = ["id", "is_active", "date_joined", "email_verified", "approval_status"]

class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    role = serializers.ChoiceField(choices=CustomUser.ROLE_CHOICES)

    class Meta:
        model = CustomUser
        fields = ["email", "password", "first_name", "last_name", "phone_number", "role"]

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name'),
            last_name=validated_data.get('last_name'),
            phone_number=validated_data.get('phone_number'),
            role=validated_data.get('role', 'enduser')
        )
        return user

class OperatorPermissionSerializer(serializers.ModelSerializer):
    app_level_permissions = PermissionSerializer(many=True)

    class Meta:
        model = OperatorPermission
        fields = ["operator", "app_level_permissions", "view_only"]
