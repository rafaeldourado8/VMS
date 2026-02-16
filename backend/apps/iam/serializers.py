from rest_framework import serializers
from apps.usuarios.models import Usuario
from .models import IAMRule, UserPermissions

class UserIAMSerializer(serializers.ModelSerializer):
    permissions = serializers.SerializerMethodField()
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Usuario
        fields = ['id', 'email', 'name', 'role', 'is_active', 'permissions', 'created_at', 'password']
        read_only_fields = ['id', 'created_at']

    def get_permissions(self, obj):
        try:
            return obj.iam_permissions.permissions
        except UserPermissions.DoesNotExist:
            return []

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = Usuario.objects.create(**validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance

class IAMRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = IAMRule
        fields = ['id', 'name', 'description', 'conditions', 'actions', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class UserPermissionsSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = UserPermissions
        fields = ['id', 'user', 'user_email', 'permissions', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
