import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from services.streaming.infrastructure.rtsp_client import RTSPClient


@pytest.fixture
def mock_mediamtx():
    client = Mock()
    client.add_path = Mock(return_value=True)
    client.get_path_status = Mock(return_value=True)
    return client


@pytest.fixture
def rtsp_client(mock_mediamtx):
    return RTSPClient("cam1", "rtsp://test.com/stream", mock_mediamtx)


@pytest.mark.asyncio
async def test_connect_success(rtsp_client, mock_mediamtx):
    """Test successful connection"""
    result = await rtsp_client.connect_with_retry()
    
    assert result is True
    assert rtsp_client.is_online is True
    assert rtsp_client.retry_count == 0
    mock_mediamtx.add_path.assert_called_once_with("cam1", "rtsp://test.com/stream")


@pytest.mark.asyncio
async def test_connect_retry_exponential_backoff(rtsp_client, mock_mediamtx):
    """Test exponential backoff: 5s → 10s → 30s → 60s"""
    mock_mediamtx.add_path.side_effect = [False, False, False, True]
    
    with patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
        result = await rtsp_client.connect_with_retry()
        
        assert result is True
        assert mock_sleep.call_count == 3
        mock_sleep.assert_any_call(5)
        mock_sleep.assert_any_call(10)
        mock_sleep.assert_any_call(30)


@pytest.mark.asyncio
async def test_connect_max_retries_offline(rtsp_client, mock_mediamtx):
    """Test marking offline after 10 failed attempts"""
    mock_mediamtx.add_path.return_value = False
    
    with patch('asyncio.sleep', new_callable=AsyncMock):
        result = await rtsp_client.connect_with_retry()
        
        assert result is False
        assert rtsp_client.is_online is False
        assert rtsp_client.retry_count == 10


@pytest.mark.asyncio
async def test_health_check_reconnect(rtsp_client, mock_mediamtx):
    """Test health check triggers reconnection"""
    rtsp_client.is_online = True
    mock_mediamtx.get_path_status.return_value = False
    mock_mediamtx.add_path.return_value = True
    
    task = asyncio.create_task(rtsp_client.health_check_loop())
    await asyncio.sleep(0.1)
    task.cancel()
    
    try:
        await task
    except asyncio.CancelledError:
        pass
    
    assert mock_mediamtx.get_path_status.called


@pytest.mark.asyncio
async def test_metric_increment(rtsp_client, mock_mediamtx):
    """Test reconnect metric increments"""
    with patch('services.streaming.infrastructure.rtsp_client.reconnect_metric') as mock_metric:
        await rtsp_client.connect_with_retry()
        
        mock_metric.labels.assert_called_with(camera_id="cam1", status="success")
        mock_metric.labels().inc.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
