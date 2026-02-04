"""
Storage Service - Indexador de Gravações + API
"""
import os
import asyncio
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import List, Optional
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncpg

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("storage")

class RecordingSegment(BaseModel):
    camera_id: int
    path: str
    start_time: datetime
    end_time: datetime
    duration_seconds: int
    file_size_bytes: int
    processed: bool = False

class RecordingQuery(BaseModel):
    camera_id: int
    start_time: datetime
    end_time: datetime

class StorageService:
    def __init__(self):
        self.recordings_path = Path("/recordings")
        self.db_pool: Optional[asyncpg.Pool] = None
    
    async def initialize(self):
        self.db_pool = await asyncpg.create_pool(
            host=os.getenv("POSTGRES_HOST", "postgres_main"),
            port=5432,
            user=os.getenv("POSTGRES_USER", "gtvision_user"),
            password=os.getenv("POSTGRES_PASSWORD", "your-secure-password-here"),
            database=os.getenv("POSTGRES_DB", "gtvision_db")
        )
        await self._create_tables()
        asyncio.create_task(self._scan_recordings_loop())
    
    async def _create_tables(self):
        async with self.db_pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS recording_segments (
                    id SERIAL PRIMARY KEY,
                    camera_id INTEGER NOT NULL,
                    file_path TEXT NOT NULL UNIQUE,
                    start_time TIMESTAMP NOT NULL,
                    end_time TIMESTAMP NOT NULL,
                    duration_seconds INTEGER NOT NULL,
                    file_size_bytes BIGINT NOT NULL,
                    processed BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT NOW()
                );
                CREATE INDEX IF NOT EXISTS idx_camera_time ON recording_segments(camera_id, start_time, end_time);
            """)
    
    async def _scan_recordings_loop(self):
        while True:
            try:
                await asyncio.sleep(60)
                await self._scan_recordings()
            except Exception as e:
                logger.error(f"Erro no scan: {e}")
    
    async def _scan_recordings(self):
        if not self.recordings_path.exists():
            return
        
        for cam_dir in self.recordings_path.iterdir():
            if not cam_dir.is_dir() or not cam_dir.name.startswith("cam_"):
                continue
            
            camera_id = int(cam_dir.name.split("_")[1])
            
            for date_dir in cam_dir.iterdir():
                if not date_dir.is_dir():
                    continue
                
                for segment_file in date_dir.glob("*.mp4"):
                    await self._index_segment(camera_id, segment_file)
    
    async def _index_segment(self, camera_id: int, file_path: Path):
        try:
            stat = file_path.stat()
            filename = file_path.stem
            parts = filename.split("-")
            date_str = file_path.parent.name
            
            start_time = datetime.strptime(
                f"{date_str} {parts[0]}:{parts[1]}:{parts[2]}", 
                "%Y-%m-%d %H:%M:%S"
            )
            end_time = start_time + timedelta(hours=1)
            duration = int((end_time - start_time).total_seconds())
            
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO recording_segments 
                    (camera_id, file_path, start_time, end_time, duration_seconds, file_size_bytes)
                    VALUES ($1, $2, $3, $4, $5, $6)
                    ON CONFLICT (file_path) DO NOTHING
                """, camera_id, str(file_path), start_time, end_time, duration, stat.st_size)
                
        except Exception as e:
            logger.error(f"Erro ao indexar {file_path}: {e}")
    
    async def query_recordings(self, query: RecordingQuery) -> List[RecordingSegment]:
        async with self.db_pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT camera_id, file_path, start_time, end_time, 
                       duration_seconds, file_size_bytes, processed
                FROM recording_segments
                WHERE camera_id = $1 
                  AND start_time <= $3 
                  AND end_time >= $2
                ORDER BY start_time
            """, query.camera_id, query.start_time, query.end_time)
            
            return [
                RecordingSegment(
                    camera_id=row["camera_id"],
                    path=row["file_path"],
                    start_time=row["start_time"],
                    end_time=row["end_time"],
                    duration_seconds=row["duration_seconds"],
                    file_size_bytes=row["file_size_bytes"],
                    processed=row["processed"]
                ) for row in rows
            ]
    
    async def mark_as_processed(self, file_path: str):
        async with self.db_pool.acquire() as conn:
            await conn.execute(
                "UPDATE recording_segments SET processed = TRUE WHERE file_path = $1",
                file_path
            )

storage_service = StorageService()

app = FastAPI(title="GT-Vision Storage Service")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.on_event("startup")
async def startup():
    await storage_service.initialize()

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/recordings/query")
async def query_recordings_endpoint(query: RecordingQuery):
    """Lista gravações direto do disco (sem banco)"""
    recordings = []
    recordings_path = Path("/recordings")
    
    if not recordings_path.exists():
        return recordings
    
    cam_dir = recordings_path / f"cam_{query.camera_id}"
    if not cam_dir.exists():
        return recordings
    
    for date_dir in sorted(cam_dir.iterdir(), reverse=True):
        if not date_dir.is_dir():
            continue
        
        for video_file in sorted(date_dir.glob("*.mp4"), reverse=True):
            try:
                stat = video_file.stat()
                filename = video_file.stem
                parts = filename.split("-")
                
                timestamp = datetime.strptime(
                    f"{date_dir.name} {parts[0]}:{parts[1]}:{parts[2]}",
                    "%Y-%m-%d %H:%M:%S"
                ).replace(tzinfo=timezone.utc)
                
                query_start = query.start_time.replace(tzinfo=timezone.utc) if query.start_time.tzinfo is None else query.start_time
                query_end = query.end_time.replace(tzinfo=timezone.utc) if query.end_time.tzinfo is None else query.end_time
                
                if query_start <= timestamp <= query_end:
                    recordings.append({
                        "camera_id": query.camera_id,
                        "path": str(video_file),
                        "start_time": timestamp.isoformat(),
                        "end_time": (timestamp + timedelta(hours=1)).isoformat(),
                        "duration_seconds": 3600,
                        "file_size_bytes": stat.st_size,
                        "processed": False
                    })
            except:
                pass
    
    return recordings[:50]

@app.post("/recordings/mark-processed")
async def mark_processed(file_path: str):
    await storage_service.mark_as_processed(file_path)
    return {"success": True}

@app.get("/recordings/stats")
async def get_stats():
    async with storage_service.db_pool.acquire() as conn:
        total = await conn.fetchval("SELECT COUNT(*) FROM recording_segments")
        processed = await conn.fetchval("SELECT COUNT(*) FROM recording_segments WHERE processed = TRUE")
        total_size = await conn.fetchval("SELECT SUM(file_size_bytes) FROM recording_segments")
        
        return {
            "total_segments": total,
            "processed_segments": processed,
            "pending_segments": total - processed,
            "total_size_gb": round((total_size or 0) / (1024**3), 2)
        }
