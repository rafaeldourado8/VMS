from ..value_objects.support_email import SupportEmail
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Configuration:
    """Entidade de domínio Configuration"""
    
    id: Optional[int]
    notifications_enabled: bool = True
    support_email: SupportEmail = SupportEmail(None)
    maintenance_mode: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def enable_notifications(self) -> None:
        """Habilita notificações"""
        self.notifications_enabled = True
    
    def disable_notifications(self) -> None:
        """Desabilita notificações"""
        self.notifications_enabled = False
    
    def enable_maintenance_mode(self) -> None:
        """Ativa modo de manutenção"""
        self.maintenance_mode = True
    
    def disable_maintenance_mode(self) -> None:
        """Desativa modo de manutenção"""
        self.maintenance_mode = False
    
    def update_support_email(self, email: Optional[str]) -> None:
        """Atualiza email de suporte"""
        self.support_email = SupportEmail(email)
    
    def is_system_available(self) -> bool:
        """Verifica se o sistema está disponível"""
        return not self.maintenance_mode