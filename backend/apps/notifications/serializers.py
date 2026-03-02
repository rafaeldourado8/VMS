from rest_framework import serializers
from .models import NotificationPreference, NotificationLog, LoginLog


class LoginLogSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_name = serializers.CharField(source='user.name', read_only=True)
    
    class Meta:
        model = LoginLog
        fields = ['id', 'user_email', 'user_name', 'ip_address', 'logged_in_at']
        read_only_fields = ['id', 'logged_in_at']


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationPreference
        fields = [
            'email_alerts',
            'push_notifications',
            'camera_offline',
            'system_alerts',
            'updated_at',
        ]
        read_only_fields = ['updated_at']


class NotificationLogSerializer(serializers.ModelSerializer):
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    
    class Meta:
        model = NotificationLog
        fields = [
            'id',
            'type',
            'type_display',
            'category',
            'category_display',
            'title',
            'message',
            'sent_at',
            'read_at',
            'success',
        ]
        read_only_fields = ['id', 'sent_at']
