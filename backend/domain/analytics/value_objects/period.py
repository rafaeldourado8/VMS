from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

class PeriodType(Enum):
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"

@dataclass(frozen=True)
class Period:
    """Value object para período de tempo"""
    
    start_date: datetime
    end_date: datetime
    
    def __post_init__(self):
        if self.start_date >= self.end_date:
            raise ValueError("Data inicial deve ser anterior à data final")
    
    @classmethod
    def last_24_hours(cls) -> 'Period':
        """Últimas 24 horas"""
        end = datetime.now()
        start = end - timedelta(hours=24)
        return cls(start, end)
    
    @classmethod
    def last_7_days(cls) -> 'Period':
        """Últimos 7 dias"""
        end = datetime.now()
        start = end - timedelta(days=7)
        return cls(start, end)
    
    @classmethod
    def last_30_days(cls) -> 'Period':
        """Últimos 30 dias"""
        end = datetime.now()
        start = end - timedelta(days=30)
        return cls(start, end)
    
    def duration_hours(self) -> float:
        """Duração em horas"""
        return (self.end_date - self.start_date).total_seconds() / 3600