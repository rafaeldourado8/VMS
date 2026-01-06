from rest_framework import permissions
from infrastructure.persistence.django.models import AuditLogModel


class CameraAccessPermission(permissions.BasePermission):
    """Usuário só acessa câmeras do seu setor"""
    
    def has_object_permission(self, request, view, obj):
        user_sectors = request.user.sectors.all()
        return obj.sector in user_sectors


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
        user_sectors = request.user.sectors.all()
        return obj.camera.sector in user_sectors
