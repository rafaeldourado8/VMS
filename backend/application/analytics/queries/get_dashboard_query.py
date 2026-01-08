from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class GetDashboardQuery:
    """Query para buscar dados do dashboard"""
    
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    period_type: str = "day"  # hour, day, week, month