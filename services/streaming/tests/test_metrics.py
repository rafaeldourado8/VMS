import pytest
from prometheus_client import REGISTRY
from services.streaming.infrastructure.metrics import (
    vms_streams_active,
    vms_stream_errors_total,
    vms_reconnect_duration_seconds
)


def test_streams_active_metric():
    """Test active streams gauge"""
    vms_streams_active.labels(camera_id='1').set(1)
    
    metric = REGISTRY.get_sample_value('vms_streams_active', {'camera_id': '1'})
    assert metric == 1


def test_stream_errors_metric():
    """Test stream errors counter"""
    before = REGISTRY.get_sample_value(
        'vms_stream_errors_total', 
        {'camera_id': '1', 'error_type': 'connection'}
    ) or 0
    
    vms_stream_errors_total.labels(camera_id='1', error_type='connection').inc()
    
    after = REGISTRY.get_sample_value(
        'vms_stream_errors_total',
        {'camera_id': '1', 'error_type': 'connection'}
    )
    
    assert after == before + 1


def test_reconnect_duration_metric():
    """Test reconnect duration histogram"""
    vms_reconnect_duration_seconds.labels(camera_id='1').observe(5.5)
    
    metric = REGISTRY.get_sample_value(
        'vms_reconnect_duration_seconds_count',
        {'camera_id': '1'}
    )
    
    assert metric >= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
