from .clip_mapper import ClipMapper
from typing import List, Optional

from apps.clips.models import Clip as ClipModel
from domain.clips import Clip, ClipRepository

class DjangoClipRepository(ClipRepository):
    """Implementação Django do repositório de clips"""
    
    def create_clip(self, clip: Clip) -> Clip:
        """Cria um novo clip"""
        model = ClipMapper.to_model(clip)
        model.save()
        return ClipMapper.to_domain(model)
    
    def get_clips_by_user(self, user_id: int) -> List[Clip]:
        """Busca clips de um usuário"""
        models = ClipModel.objects.filter(owner_id=user_id).order_by('-created_at')
        return [ClipMapper.to_domain(model) for model in models]
    
    def get_clip_by_id(self, clip_id: int) -> Optional[Clip]:
        """Busca clip por ID"""
        try:
            model = ClipModel.objects.get(id=clip_id)
            return ClipMapper.to_domain(model)
        except ClipModel.DoesNotExist:
            return None
    
    def delete_clip(self, clip_id: int) -> bool:
        """Remove um clip"""
        try:
            ClipModel.objects.get(id=clip_id).delete()
            return True
        except ClipModel.DoesNotExist:
            return False