from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class Recording:
    id: str
    camera_id: str
    file_path: str
    started_at: datetime
    size_bytes: int
    is_permanent: bool = False
    ended_at: datetime | None = None
    
    def should_delete(self, retention_days: int) -> bool:
        """Verifica se deve ser deletado."""
        if self.is_permanent:
            return False
        age = datetime.now() - self.started_at
        return age.days >= retention_days
    
    def expires_in_days(self, retention_days: int) -> int:
        """Dias até expiração."""
        if self.is_permanent:
            return -1
        age = datetime.now() - self.started_at
        return max(0, retention_days - age.days)
    
    def mark_permanent(self) -> None:
        """Marca como permanente (clipe)."""
        self.is_permanent = True
