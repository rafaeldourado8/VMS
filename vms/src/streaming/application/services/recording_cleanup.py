from domain.repositories.recording_repository import IRecordingRepository

class RecordingCleanupService:
    """Serviço para limpeza de gravações expiradas"""
    
    def __init__(self, recording_repo: IRecordingRepository):
        self._recording_repo = recording_repo
    
    def cleanup_expired(self, retention_days: int) -> int:
        """
        Remove gravações expiradas (não permanentes)
        Returns: quantidade de gravações deletadas
        """
        # Lista gravações que expiram em 1 dia (para notificar)
        expiring = self._recording_repo.list_expiring_soon(retention_days, days_before=1)
        
        deleted_count = 0
        for recording in expiring:
            if recording.should_delete(retention_days):
                self._recording_repo.delete(recording.id)
                deleted_count += 1
        
        return deleted_count
    
    def get_expiring_soon(self, retention_days: int) -> list:
        """Retorna gravações que expiram em 1 dia"""
        return self._recording_repo.list_expiring_soon(retention_days, days_before=1)
