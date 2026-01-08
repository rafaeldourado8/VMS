from .permissions import IsAdminOrReadOnly
from .serializers import UsuarioSerializer, MyTokenObtainPairSerializer

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
        query = ListUsersQuery(active_only=True)
        users = self.list_handler.handle(query)
        from apps.usuarios.models import Usuario
        return Usuario.objects.filter(id__in=[u.id for u in users])

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            command = CreateUserCommand(**serializer.validated_data)
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
    """View de autenticação usando DDD"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.auth_service = AuthenticationService(DjangoUserRepository())
    
    def post(self, request, *args, **kwargs):
        try:
            email = request.data.get('email')
            password = request.data.get('password')
            
            if not email or not password:
                return Response(
                    {"detail": "Email e senha são obrigatórios"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            result = self.auth_service.authenticate_user(email, password)
            return Response(result, status=status.HTTP_200_OK)
            
        except UserDomainException as e:
            return Response(
                {"detail": str(e)}, 
                status=status.HTTP_401_UNAUTHORIZED
            )

class LogoutAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request):
        try:
            token = RefreshToken(request.data["refresh_token"])
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except:
            return Response({"error": "Token inválido."}, status=status.HTTP_400_BAD_REQUEST)