from admin.domain import IUserRepository
from admin.infrastructure.jwt.jwt_service import JWTService
from admin.application.use_cases.create_user import CreateUserUseCase
from admin.application.use_cases.authenticate_user import AuthenticateUserUseCase
from admin.application.use_cases.update_user_permissions import UpdateUserPermissionsUseCase


class Container:
    def __init__(self, jwt_secret: str = "dev-secret-key"):
        self._instances = {}
        self._jwt_secret = jwt_secret
    
    def get_user_repository(self) -> IUserRepository:
        if "user_repo" not in self._instances:
            # Lazy import para evitar dependência de Django em testes
            try:
                from admin.infrastructure.django.repository import DjangoUserRepository
                self._instances["user_repo"] = DjangoUserRepository()
            except ImportError:
                # Fallback para testes
                from admin.tests.conftest import InMemoryUserRepository
                self._instances["user_repo"] = InMemoryUserRepository()
        return self._instances["user_repo"]
    
    def get_jwt_service(self) -> JWTService:
        if "jwt_service" not in self._instances:
            self._instances["jwt_service"] = JWTService(
                secret_key=self._jwt_secret,
                expires_in=3600
            )
        return self._instances["jwt_service"]
    
    def get_create_user_use_case(self) -> CreateUserUseCase:
        return CreateUserUseCase(self.get_user_repository())
    
    def get_authenticate_user_use_case(self) -> AuthenticateUserUseCase:
        return AuthenticateUserUseCase(
            self.get_user_repository(),
            self.get_jwt_service()
        )
    
    def get_update_user_permissions_use_case(self) -> UpdateUserPermissionsUseCase:
        return UpdateUserPermissionsUseCase(self.get_user_repository())


# Singleton
container = Container()
