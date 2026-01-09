"""
Teste unitário do SnapshotWorker
"""
import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from workers.snapshot_worker import SnapshotWorker, SnapshotCache


@pytest.fixture
def mock_redis():
    redis = Mock()
    redis.setex = Mock()
    return redis


@pytest.fixture
def snapshot_cache(mock_redis):
    return SnapshotCache(mock_redis, ttl=60)


@pytest.fixture
def snapshot_worker(mock_redis):
    with patch('workers.snapshot_worker.Redis') as mock_redis_class:
        mock_redis_class.from_url.return_value = mock_redis
        worker = SnapshotWorker("redis://localhost:6379")
        return worker


def test_snapshot_cache_set(snapshot_cache, mock_redis):
    """Testa se o cache salva snapshot corretamente"""
    camera_id = "1"
    image_bytes = b"fake_image_data"
    
    snapshot_cache.set(camera_id, image_bytes)
    
    mock_redis.setex.assert_called_once_with("snapshot:1", 60, image_bytes)


def test_add_camera(snapshot_worker):
    """Testa adição de câmera"""
    snapshot_worker.add_camera("1", "rtsp://test.com/stream")
    
    assert "1" in snapshot_worker.active_cameras
    assert snapshot_worker.active_cameras["1"] == "rtsp://test.com/stream"


def test_remove_camera(snapshot_worker):
    """Testa remoção de câmera"""
    snapshot_worker.add_camera("1", "rtsp://test.com/stream")
    snapshot_worker.remove_camera("1")
    
    assert "1" not in snapshot_worker.active_cameras


@pytest.mark.asyncio
async def test_extract_snapshot_success(snapshot_worker):
    """Testa extração de snapshot com sucesso"""
    fake_image = b"\xff\xd8\xff\xe0fake_jpeg_data\xff\xd9"
    
    with patch('asyncio.create_subprocess_exec') as mock_subprocess:
        mock_process = AsyncMock()
        mock_process.communicate = AsyncMock(return_value=(fake_image, b""))
        mock_subprocess.return_value = mock_process
        
        result = await snapshot_worker.extract_snapshot("1", "rtsp://test.com/stream")
        
        assert result == fake_image


@pytest.mark.asyncio
async def test_extract_snapshot_timeout(snapshot_worker):
    """Testa timeout na extração de snapshot"""
    with patch('asyncio.create_subprocess_exec') as mock_subprocess:
        mock_process = AsyncMock()
        mock_process.communicate = AsyncMock(side_effect=asyncio.TimeoutError())
        mock_subprocess.return_value = mock_process
        
        result = await snapshot_worker.extract_snapshot("1", "rtsp://test.com/stream")
        
        assert result is None


@pytest.mark.asyncio
async def test_process_camera(snapshot_worker):
    """Testa processamento de câmera"""
    snapshot_worker.running = True
    snapshot_worker.add_camera("1", "rtsp://test.com/stream")
    
    fake_image = b"fake_image"
    
    with patch.object(snapshot_worker, 'extract_snapshot', return_value=fake_image) as mock_extract:
        with patch.object(snapshot_worker.cache, 'set') as mock_cache_set:
            # Executar por 1 iteração apenas
            task = asyncio.create_task(snapshot_worker.process_camera("1", "rtsp://test.com/stream"))
            await asyncio.sleep(0.1)
            snapshot_worker.running = False
            await task
            
            mock_extract.assert_called()
            mock_cache_set.assert_called_with("1", fake_image)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
