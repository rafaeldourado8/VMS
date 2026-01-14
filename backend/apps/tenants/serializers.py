from rest_framework import serializers
from .models import Organization, Subscription

class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ['id', 'name', 'slug', 'database_name', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']

class SubscriptionSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    
    class Meta:
        model = Subscription
        fields = [
            'id', 'organization', 'organization_name', 'plan', 
            'recording_days', 'max_cameras', 'max_users', 'max_clips',
            'max_concurrent_streams', 'is_active', 'started_at', 'expires_at'
        ]
        read_only_fields = ['id', 'recording_days', 'max_cameras', 'max_users', 'max_clips', 'max_concurrent_streams']
