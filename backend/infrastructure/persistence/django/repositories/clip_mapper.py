from apps.clips.models import Clip as ClipModel
from domain.clips.entities.clip import Clip

class ClipMapper:
    """Mapper entre domínio e modelo Django para Clips"""
    
    @staticmethod
    def to_domain(model: ClipModel) -> Clip:
        """Converte modelo Django para entidade de domínio"""
        return Clip(
            id=model.id,
            owner_id=model.owner_id,
            camera_id=model.camera_id,
            name=model.name,
            start_time=model.start_time,
            end_time=model.end_time,
            file_path=model.file_path,
            thumbnail_path=model.thumbnail_path,
            duration_seconds=model.duration_seconds,
            created_at=model.created_at
        )
    
    @staticmethod
    def to_model(entity: Clip) -> ClipModel:
        """Converte entidade de domínio para modelo Django"""
        return ClipModel(
            id=entity.id,
            owner_id=entity.owner_id,
            camera_id=entity.camera_id,
            name=entity.name,
            start_time=entity.start_time,
            end_time=entity.end_time,
            file_path=entity.file_path,
            thumbnail_path=entity.thumbnail_path,
            duration_seconds=entity.duration_seconds,
            created_at=entity.created_at
        )