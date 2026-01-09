import asyncpg
import json
from typing import Optional
from domain.detection_result import DetectionResult
import logging

logger = logging.getLogger(__name__)


class DetectionRepository:
    def __init__(self, db_url: str):
        self.db_url = db_url
        self.pool: Optional[asyncpg.Pool] = None
    
    async def connect(self):
        self.pool = await asyncpg.create_pool(self.db_url, min_size=1, max_size=5)
        await self._create_table()
        logger.info("DetectionRepository connected")
    
    async def _create_table(self):
        async with self.pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS detection_results (
                    id SERIAL PRIMARY KEY,
                    camera_id VARCHAR(100) NOT NULL,
                    timestamp TIMESTAMP NOT NULL,
                    provider VARCHAR(50) NOT NULL,
                    detections JSONB NOT NULL,
                    confidence_avg FLOAT,
                    frame_id VARCHAR(100),
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_detection_camera_timestamp 
                ON detection_results(camera_id, timestamp DESC)
            """)
    
    async def save(self, result: DetectionResult) -> int:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("""
                INSERT INTO detection_results 
                (camera_id, timestamp, provider, detections, confidence_avg, frame_id)
                VALUES ($1, $2, $3, $4, $5, $6)
                RETURNING id
            """, result.camera_id, result.timestamp, result.provider, 
                json.dumps(result.detections), result.confidence_avg, result.frame_id)
            return row['id']
    
    async def close(self):
        if self.pool:
            await self.pool.close()
