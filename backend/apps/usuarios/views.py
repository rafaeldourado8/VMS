from .permissions import IsAdminOrReadOnly
from .serializers import UsuarioSerializer, MyTokenObtainPairSerializer
from .plan_serializers import PlanInfoSerializer
from apps.tenants.permissions import CanManageUsers, IsOrganizationAdmin

from infrastructure.persistence.django.repositories import DjangoUserRepository
from infrastructure.auth.authentication_service import AuthenticationService
from rest_framework import permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from application.user import (
    CreateUserHandler, GetUserHandler, ListUsersHandler, UpdateUserHandler, DeleteUserHandler,
    CreateUserCommand, GetUserQuery, ListUsersQuery, UpdateUserCommand, DeleteUserCommand,
    UserPermissions
)
from domain.user.exceptions import UserDomainException

class UsuarioViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = UsuarioSerializer
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        repo = DjangoUserRepository()
        self.create_handler = CreateUserHandler(repo)
        self.get_handler = GetUserHandler(repo)
        self.list_handler = ListUsersHandler(repo)
        self.update_handler = UpdateUserHandler(repo)
        self.delete_handler = DeleteUserHandler(repo)

    def get_queryset(self):
        # Admin vê apenas usuários da sua organização
        if self.request.user.role == 'admin' and self.request.user.organization:
            from apps.usuarios.models import Usuario
            return Usuario.objects.filter(organization=self.request.user.organization)
        
        query = ListUsersQuery(active_only=True)
        users = self.list_handler.handle(query)
        from apps.usuarios.models import Usuario
        return Usuario.objects.filter(id__in=[u.id for u in users])
    
    def get_permissions(self):
        if self.action == 'create':
            return [CanManageUsers()]
        return super().get_permissions()

    def create(self, request, *args, **kwargs):
        # Verificar limite de usuários
        org = request.user.organization
        if org and hasattr(org, 'subscription'):
            current_users = org.users.count()
            max_users = org.subscription.max_users
            if current_users >= max_users:
                return Response(
                    {"detail": f"Limite de {max_users} usuários atingido para o plano {org.subscription.plan}"},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            # Forçar organização do admin
            validated_data = serializer.validated_data
            validated_data['organization'] = request.user.organization
            
            command = CreateUserCommand(**validated_data)
            user = self.create_handler.handle(command)
            
            from apps.usuarios.models import Usuario
            user_model = Usuario.objects.get(id=user.id)
            output = self.get_serializer(user_model)
            return Response(output.data, status=status.HTTP_201_CREATED)
        except UserDomainException as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    def retrieve(self, request, *args, **kwargs):
        try:
            query = GetUserQuery(user_id=int(kwargs['pk']))
            user = self.get_handler.handle(query)
            
            from apps.usuarios.models import Usuario
            user_model = Usuario.objects.get(id=user.id)
            serializer = self.get_serializer(user_model)
            return Response(serializer.data)
        except UserDomainException as e:
            return Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)
    
    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, partial=kwargs.get('partial', False))
        serializer.is_valid(raise_exception=True)
        
        try:
            command = UpdateUserCommand(
                user_id=int(kwargs['pk']),
                **serializer.validated_data
            )
            user = self.update_handler.handle(command)
            
            from apps.usuarios.models import Usuario
            user_model = Usuario.objects.get(id=user.id)
            output = self.get_serializer(user_model)
            return Response(output.data)
        except UserDomainException as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, *args, **kwargs):
        try:
            command = DeleteUserCommand(user_id=int(kwargs['pk']))
            self.delete_handler.handle(command)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except UserDomainException as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class MeAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        serializer = UsuarioSerializer(request.user)
        return Response(serializer.data)

class MyTokenObtainPairView(TokenObtainPairView):
    """View de autenticação usando serializer customizado"""
    serializer_class = MyTokenObtainPairSerializer
    
    def post(self, request, *args, **kwargs):
        # Converte 'email' para 'username' para compatibilidade com JWT
        if 'email' in request.data:
            request.data['username'] = request.data['email']
        return super().post(request, *args, **kwargs)

class LogoutAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request):
        try:
            token = RefreshToken(request.data["refresh_token"])
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except:
            return Response({"error": "Token inválido."}, status=status.HTTP_400_BAD_REQUEST)

class PlanInfoAPIView(APIView):
    """Retorna informações do plano do usuário"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        from apps.cameras.models import Camera
        
        current_cameras = Camera.objects.filter(owner=user).count()
        
        data = {
            'plan': user.plan,
            'recording_days': user.recording_days,
            'max_cameras': user.max_cameras,
            'max_clips': user.max_clips,
            'max_concurrent_streams': user.max_concurrent_streams,
            'current_cameras': current_cameras,
            'can_add_camera': current_cameras < user.max_cameras,
        }
        
        serializer = PlanInfoSerializer(data)
        return Response(serializer.data)