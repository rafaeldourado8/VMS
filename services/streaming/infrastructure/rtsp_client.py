import asyncio
import logging
import time
from typing import Optional
from prometheus_client import Counter

logger = logging.getLogger(__name__)

reconnect_metric = Counter(
    'vms_camera_reconnect_total',
    'Total camera reconnection attempts',
    ['camera_id', 'status']
)


class RTSPClient:
    """RTSP client with auto-reconnection and health checks"""
    
    MAX_RETRIES = 10
    BACKOFF_INTERVALS = [5, 10, 30, 60]
    HEALTH_CHECK_INTERVAL = 30
    
    def __init__(self, camera_id: str, rtsp_url: str, mediamtx_client):
        self.camera_id = camera_id
        self.rtsp_url = rtsp_url
        self.mediamtx = mediamtx_client
        self.retry_count = 0
        self.is_online = False
        self._health_task: Optional[asyncio.Task] = None
    
    async def connect_with_retry(self) -> bool:
        """Connect with exponential backoff"""
        self.retry_count = 0
        
        while self.retry_count < self.MAX_RETRIES:
            try:
                logger.info(f"🔄 Connecting camera {self.camera_id} (attempt {self.retry_count + 1}/{self.MAX_RETRIES})")
                
                if self.mediamtx.add_path(self.camera_id, self.rtsp_url):
                    self.is_online = True
                    self.retry_count = 0
                    reconnect_metric.labels(camera_id=self.camera_id, status='success').inc()
                    logger.info(f"✅ Camera {self.camera_id} connected")
                    return True
                
                raise Exception("MediaMTX add_path failed")
                
            except Exception as e:
                self.retry_count += 1
                reconnect_metric.labels(camera_id=self.camera_id, status='failed').inc()
                
                if self.retry_count >= self.MAX_RETRIES:
                    self.is_online = False
                    logger.error(f"❌ Camera {self.camera_id} offline after {self.MAX_RETRIES} attempts")
                    return False
                
                backoff = self.BACKOFF_INTERVALS[min(self.retry_count - 1, len(self.BACKOFF_INTERVALS) - 1)]
                logger.warning(f"⏳ Retry {self.retry_count}/{self.MAX_RETRIES} in {backoff}s: {e}")
                await asyncio.sleep(backoff)
        
        return False
    
    async def health_check_loop(self):
        """Periodic health check every 30s"""
        while True:
            await asyncio.sleep(self.HEALTH_CHECK_INTERVAL)
            
            try:
                status = self.mediamtx.get_path_status(self.camera_id)
                
                if not status:
                    logger.warning(f"⚠️ Camera {self.camera_id} health check failed, reconnecting...")
                    self.is_online = False
                    await self.connect_with_retry()
                else:
                    if not self.is_online:
                        self.is_online = True
                        logger.info(f"✅ Camera {self.camera_id} recovered")
                        
            except Exception as e:
                logger.error(f"❌ Health check error for {self.camera_id}: {e}")
    
    def start_health_check(self):
        """Start background health check task"""
        if not self._health_task or self._health_task.done():
            self._health_task = asyncio.create_task(self.health_check_loop())
    
    def stop_health_check(self):
        """Stop health check task"""
        if self._health_task and not self._health_task.done():
            self._health_task.cancel()
