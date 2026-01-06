from rest_framework import permissions
from django.utils import timezone
from infrastructure.persistence.django.models import AuditLogModel


class CameraAccessPermission(permissions.BasePermission):
    """Usuário só acessa câmeras do seu setor"""
    
    def has_object_permission(self, request, view, obj):
        return obj.sector in request.user.sectors.all()


class RecordingAccessPermission(permissions.BasePermission):
    """Log obrigatório para acesso a gravações (LGPD Art. 37)"""
    
    def has_object_permission(self, request, view, obj):
        AuditLogModel.objects.create(
            user=request.user,
            action='view_recording',
            resource=f'camera_{obj.camera.id}',
            ip_address=request.META.get('REMOTE_ADDR', '0.0.0.0'),
            details={
                'camera_name': obj.camera.name,
                'recording_id': obj.id
            }
        )
        return obj.camera.sector in request.user.sectors.all()
