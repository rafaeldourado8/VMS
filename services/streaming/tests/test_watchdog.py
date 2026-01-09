import pytest
import asyncio
import time
from unittest.mock import Mock, patch, AsyncMock
from infrastructure.watchdog import StreamWatchdog


@pytest.fixture
def watchdog():
    return StreamWatchdog("amqp://test")


def test_update_frame(watchdog):
    """Test frame timestamp update"""
    watchdog.update_frame("cam1")
    
    assert "cam1" in watchdog.frame_timestamps
    assert watchdog.frame_timestamps["cam1"] > 0


@pytest.mark.asyncio
async def test_detect_frozen_stream(watchdog):
    """Test frozen stream detection after 30s"""
    watchdog.update_frame("cam1")
    watchdog.frame_timestamps["cam1"] = time.time() - 35
    
    with patch.object(watchdog, '_publish_frozen_event', new_callable=AsyncMock) as mock_publish:
        await watchdog.check_streams()
        
        mock_publish.assert_called_once_with("cam1")
        assert "cam1" not in watchdog.frame_timestamps


@pytest.mark.asyncio
async def test_no_detection_for_active_stream(watchdog):
    """Test no detection for active streams"""
    watchdog.update_frame("cam1")
    
    with patch.object(watchdog, '_publish_frozen_event', new_callable=AsyncMock) as mock_publish:
        await watchdog.check_streams()
        
        mock_publish.assert_not_called()
        assert "cam1" in watchdog.frame_timestamps


@pytest.mark.asyncio
async def test_publish_frozen_event(watchdog):
    """Test RabbitMQ event publishing"""
    with patch('pika.BlockingConnection') as mock_conn:
        mock_channel = Mock()
        mock_conn.return_value.channel.return_value = mock_channel
        
        await watchdog._publish_frozen_event("cam1")
        
        mock_channel.exchange_declare.assert_called_once()
        mock_channel.basic_publish.assert_called_once()


@pytest.mark.asyncio
async def test_metric_increment(watchdog):
    """Test frozen metric increments"""
    watchdog.update_frame("cam1")
    watchdog.frame_timestamps["cam1"] = time.time() - 35
    
    with patch('infrastructure.watchdog.frozen_metric') as mock_metric:
        with patch.object(watchdog, '_publish_frozen_event', new_callable=AsyncMock):
            await watchdog.check_streams()
            
            mock_metric.labels.assert_called_with(camera_id="cam1")
            mock_metric.labels().inc.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
