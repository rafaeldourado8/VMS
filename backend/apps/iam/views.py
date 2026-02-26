from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from django.shortcuts import get_object_or_404
from apps.usuarios.models import Usuario
from .models import IAMRule, UserPermissions, TenantIsolation
from .serializers import UserIAMSerializer, IAMRuleSerializer, UserPermissionsSerializer
from .middleware import get_user_resources, check_user_permission, grant_user_access
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed

class UserIAMViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UserIAMSerializer
    permission_classes = [IsAdminUser]

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Criar UserPermissions se não existir
        permissions = request.data.get('permissions', [])
        UserPermissions.objects.update_or_create(
            user=user,
            defaults={'permissions': permissions}
        )
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        # Atualizar permissões
        permissions = request.data.get('permissions')
        if permissions is not None:
            UserPermissions.objects.update_or_create(
                user=user,
                defaults={'permissions': permissions}
            )
        
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def grant_resource_access(self, request, pk=None):
        """Concede acesso a um recurso específico"""
        user = self.get_object()
        resource_type = request.data.get('resource_type')
        resource_id = request.data.get('resource_id')
        can_read = request.data.get('can_read', True)
        can_write = request.data.get('can_write', False)
        can_delete = request.data.get('can_delete', False)
        
        grant_user_access(user, resource_type, resource_id, can_read, can_write, can_delete)
        
        return Response({'status': 'access granted'})

    @action(detail=True, methods=['get'])
    def resources(self, request, pk=None):
        """Lista recursos que o usuário tem acesso"""
        user = self.get_object()
        resource_type = request.query_params.get('type')
        
        if resource_type:
            isolations = TenantIsolation.objects.filter(user=user, resource_type=resource_type)
        else:
            isolations = TenantIsolation.objects.filter(user=user)
        
        data = [{
            'resource_type': iso.resource_type,
            'resource_id': iso.resource_id,
            'can_read': iso.can_read,
            'can_write': iso.can_write,
            'can_delete': iso.can_delete,
        } for iso in isolations]
        
        return Response(data)

class IAMRuleViewSet(viewsets.ModelViewSet):
    queryset = IAMRule.objects.all()
    serializer_class = IAMRuleSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.query_params.get('active_only') == 'true':
            queryset = queryset.filter(is_active=True)
        return queryset

class UserPermissionsViewSet(viewsets.ModelViewSet):
    queryset = UserPermissions.objects.all()
    serializer_class = UserPermissionsSerializer
    permission_classes = [IsAdminUser]

    @action(detail=False, methods=['get'], url_path='user/(?P<user_id>[^/.]+)')
    def get_user_permissions(self, request, user_id=None):
        user = get_object_or_404(Usuario, id=user_id)
        try:
            perms = UserPermissions.objects.get(user=user)
            serializer = self.get_serializer(perms)
            return Response(serializer.data)
        except UserPermissions.DoesNotExist:
            return Response({'permissions': []})

    @action(detail=False, methods=['post'], url_path='user/(?P<user_id>[^/.]+)')
    def update_user_permissions(self, request, user_id=None):
        user = get_object_or_404(Usuario, id=user_id)
        permissions = request.data.get('permissions', [])
        
        perms, created = UserPermissions.objects.update_or_create(
            user=user,
            defaults={'permissions': permissions}
        )
        
        serializer = self.get_serializer(perms)
        return Response(serializer.data)

@api_view(['GET', 'HEAD'])
@permission_classes([AllowAny])
def validate_token(request):
    """Valida token JWT para Nginx auth_request"""
    auth_header = request.headers.get('Authorization')
    
    if not auth_header or not auth_header.startswith('Bearer '):
        return Response(status=401)
    
    try:
        jwt_auth = JWTAuthentication()
        validated_token = jwt_auth.get_validated_token(auth_header.split(' ')[1])
        user = jwt_auth.get_user(validated_token)
        
        if user and user.is_active:
            return Response(status=200)
        return Response(status=401)
    except (AuthenticationFailed, Exception):
        return Response(status=401)
