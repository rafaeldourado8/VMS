from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Permite acesso de escrita (POST, PUT, DELETE) apenas para usuários com role 'admin'.
    Permite acesso de leitura (GET) para qualquer usuário autenticado.
    """

    def has_permission(self, request, view):
        # 1. Qualquer método seguro (GET, HEAD, OPTIONS) requer APENAS autenticação
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated

        # 2. Para métodos não seguros (POST, PUT, DELETE), exige autenticação E role 'admin'
        # Usamos request.user.is_active para garantir que o usuário não esteja bloqueado
        return (
            request.user.is_authenticated
            and request.user.is_active
            and request.user.role == "admin"
        )
