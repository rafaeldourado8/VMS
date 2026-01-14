from dataclasses import dataclass

@dataclass
class City:
    id: str
    name: str
    slug: str
    plan: str  # 'basic', 'pro', 'premium'
    max_cameras: int = 1000
    max_lpr_cameras: int = 20
    
    @property
    def retention_days(self) -> int:
        return {'basic': 7, 'pro': 15, 'premium': 30}[self.plan]
    
    @property
    def max_users(self) -> int:
        return {'basic': 3, 'pro': 5, 'premium': 10}[self.plan]
    
    def can_add_camera(self, current_count: int) -> bool:
        return current_count < self.max_cameras
    
    def can_add_lpr_camera(self, current_lpr_count: int) -> bool:
        return current_lpr_count < self.max_lpr_cameras
