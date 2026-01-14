import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from domain.value_objects.plan_type import PlanType

def test_plan_type_values():
    assert PlanType.BASIC.value == 'basic'
    assert PlanType.PRO.value == 'pro'
    assert PlanType.PREMIUM.value == 'premium'

def test_plan_type_retention_days():
    assert PlanType.BASIC.retention_days == 7
    assert PlanType.PRO.retention_days == 15
    assert PlanType.PREMIUM.retention_days == 30

def test_plan_type_max_users():
    assert PlanType.BASIC.max_users == 3
    assert PlanType.PRO.max_users == 5
    assert PlanType.PREMIUM.max_users == 10

def test_plan_type_display_name():
    assert PlanType.BASIC.display_name == 'Basic'
    assert PlanType.PRO.display_name == 'Pro'
    assert PlanType.PREMIUM.display_name == 'Premium'
