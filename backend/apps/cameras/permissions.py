from rest_framework import permissions

class CameraAccessPermission(permissions.BasePermission):
    """Permissão para acesso a câmeras"""
    
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user

class RecordingAccessPermission(permissions.BasePermission):
    """Permissão para acesso a gravações"""
    
    def has_object_permission(self, request, view, obj):
        return obj.camera.owner == request.user
