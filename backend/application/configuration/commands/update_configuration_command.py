from dataclasses import dataclass
from typing import Optional

@dataclass
class UpdateConfigurationCommand:
    """Command para atualizar configuração global"""
    
    notifications_enabled: Optional[bool] = None
    support_email: Optional[str] = None
    maintenance_mode: Optional[bool] = None