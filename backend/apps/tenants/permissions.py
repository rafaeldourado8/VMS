from rest_framework.permissions import BasePermission

class IsPlatformAdmin(BasePermission):
    """Apenas superusers (platform admins) podem acessar"""
    def has_permission(self, request, view):
        return request.user and request.user.is_superuser

class IsOrganizationAdmin(BasePermission):
    """Apenas admins da organização podem acessar"""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'admin'

class IsOrganizationMember(BasePermission):
    """Qualquer membro da organização pode acessar"""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.organization

class CanManageUsers(BasePermission):
    """Admin pode criar até 5 usuários baseado no plano"""
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.user.role != 'admin':
            return False
        
        # Verificar limite de usuários no plano
        if request.method == 'POST':
            org = request.user.organization
            if org and hasattr(org, 'subscription'):
                current_users = org.users.count()
                max_users = org.subscription.max_users
                if current_users >= max_users:
                    return False
        
        return True
