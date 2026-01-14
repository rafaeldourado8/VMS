from streaming.domain.entities.recording import Recording


class RecordingCleanupService:
    def __init__(self, recording_repo):
        self._repo = recording_repo
    
    async def cleanup_expired(self, retention_days: int) -> int:
        """Remove gravações expiradas."""
        recordings = await self._repo.list_all()
        deleted = 0
        
        for recording in recordings:
            if recording.should_delete(retention_days):
                await self._repo.delete(recording.id)
                deleted += 1
        
        return deleted
