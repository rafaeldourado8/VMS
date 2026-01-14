from enum import Enum

class PlanType(Enum):
    BASIC = 'basic'
    PRO = 'pro'
    PREMIUM = 'premium'
    
    @property
    def retention_days(self) -> int:
        return {
            PlanType.BASIC: 7,
            PlanType.PRO: 15,
            PlanType.PREMIUM: 30
        }[self]
    
    @property
    def max_users(self) -> int:
        return {
            PlanType.BASIC: 3,
            PlanType.PRO: 5,
            PlanType.PREMIUM: 10
        }[self]
    
    @property
    def display_name(self) -> str:
        return {
            PlanType.BASIC: 'Basic',
            PlanType.PRO: 'Pro',
            PlanType.PREMIUM: 'Premium'
        }[self]
