"""
Storage Service - Indexador de Gravações + API
"""
import os
import asyncio
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import List, Optional
import logging

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
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
        logger.info("Executando scan inicial...")
        await self._scan_recordings()
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
            logger.warning(f"Diretório {self.recordings_path} não existe")
            return
        
        total_indexed = 0
        for cam_dir in self.recordings_path.iterdir():
            if not cam_dir.is_dir():
                continue
            
            if cam_dir.name.startswith("cam_"):
                camera_id = int(cam_dir.name.split("_")[1])
            elif cam_dir.name.startswith("camera_"):
                camera_id = int(cam_dir.name.split("_")[1])
            else:
                continue
            
            logger.info(f"Scaneando {cam_dir.name} (camera_id={camera_id})")
            
            for date_dir in cam_dir.iterdir():
                if not date_dir.is_dir():
                    continue
                
                for segment_file in date_dir.glob("*.mp4"):
                    await self._index_segment(camera_id, segment_file)
                    total_indexed += 1
        
        logger.info(f"Scan completo: {total_indexed} segmentos processados")
    
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
            end_time = start_time + timedelta(seconds=60)
            duration = 60
            
            async with self.db_pool.acquire() as conn:
                result = await conn.execute("""
                    INSERT INTO recording_segments 
                    (camera_id, file_path, start_time, end_time, duration_seconds, file_size_bytes)
                    VALUES ($1, $2, $3, $4, $5, $6)
                    ON CONFLICT (file_path) DO NOTHING
                """, camera_id, str(file_path), start_time, end_time, duration, stat.st_size)
                
                if "INSERT" in result:
                    logger.debug(f"Indexado: {file_path.name} (camera {camera_id})")
                
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
    """Query segmentos e monta blocos com gaps"""
    segments = await storage_service.query_recordings(query)
    
    if not segments:
        return {"blocks": [], "gaps": []}
    
    blocks = []
    gaps = []
    
    for i, seg in enumerate(segments):
        if i > 0:
            prev_end = segments[i-1].end_time
            gap_seconds = (seg.start_time - prev_end).total_seconds()
            if gap_seconds > 60:
                gaps.append({
                    "start": prev_end.isoformat(),
                    "end": seg.start_time.isoformat(),
                    "duration_seconds": int(gap_seconds)
                })
        
        blocks.append({
            "start_time": seg.start_time.isoformat(),
            "end_time": seg.end_time.isoformat(),
            "duration_seconds": seg.duration_seconds,
            "file_path": f"/recordings/camera_{seg.camera_id}/{seg.start_time.strftime('%Y-%m-%d')}/{seg.start_time.strftime('%H-%M-%S')}.mp4",
            "file_size_bytes": seg.file_size_bytes
        })
    
    return {"blocks": blocks, "gaps": gaps}

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

@app.get("/timeline/{camera_id}")
async def get_timeline(camera_id: int, date: str = None, limit: int = 100):
    """Timeline com metadados leves - apenas blocos de tempo"""
    logger.info(f"[Timeline] Requisição para camera_id={camera_id}, date={date}, limit={limit}")
    
    if date:
        start = datetime.strptime(date, "%Y-%m-%d")
        end = start + timedelta(days=1)
    else:
        # Apenas últimas 24h
        end = datetime.now()
        start = end - timedelta(hours=24)
    
    query = RecordingQuery(camera_id=camera_id, start_time=start, end_time=end)
    segments = await storage_service.query_recordings(query)
    
    # Limitar resultados
    segments = segments[:limit]
    
    logger.info(f"[Timeline] Retornando {len(segments)} segmentos (limit={limit})")
    
    # Retornar apenas metadados essenciais
    blocks = []
    for seg in segments:
        blocks.append({
            "start_time": seg.start_time.isoformat(),
            "end_time": seg.end_time.isoformat(),
            "duration_seconds": seg.duration_seconds,
            "file_path": f"/recordings/camera_{seg.camera_id}/{seg.start_time.strftime('%Y-%m-%d')}/{seg.start_time.strftime('%H-%M-%S')}.mp4",
            "file_size_bytes": seg.file_size_bytes
        })
    
    return {"blocks": blocks, "total": len(segments)}

@app.get("/stream/{camera_id}")
async def stream_segments(camera_id: int, start_date: str, start_hour: int, end_hour: int):
    """Retorna segmentos em fila para streaming progressivo"""
    date = datetime.strptime(start_date, "%Y-%m-%d")
    start_time = date.replace(hour=start_hour, minute=0, second=0)
    end_time = date.replace(hour=end_hour, minute=59, second=59)
    
    query = RecordingQuery(camera_id=camera_id, start_time=start_time, end_time=end_time)
    segments = await storage_service.query_recordings(query)
    
    queue = []
    for idx, seg in enumerate(segments, 1):
        queue.append({
            "sequence": idx,
            "url": f"http://localhost:8003/download/{seg.camera_id}/{seg.start_time.strftime('%Y-%m-%d')}/{seg.start_time.strftime('%H-%M-%S')}",
            "start_time": seg.start_time.isoformat(),
            "duration": seg.duration_seconds
        })
    
    return {"queue": queue, "total": len(queue)}

@app.get("/recordings/available-dates/{camera_id}")
async def get_available_dates(camera_id: int):
    """Retorna datas com pelo menos 5 minutos de gravação"""
    async with storage_service.db_pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT DATE(start_time) as date, COUNT(*) as segment_count
            FROM recording_segments
            WHERE camera_id = $1
            GROUP BY DATE(start_time)
            HAVING COUNT(*) >= 5
            ORDER BY date DESC
        """, camera_id)
        
        return {"dates": [row["date"].isoformat() for row in rows]}

@app.get("/recordings/retention-status")
async def get_retention_status():
    """Status de retenção por câmera"""
    recordings_path = Path("/recordings")
    if not recordings_path.exists():
        return {"error": "Diretório de gravações não existe"}
    
    cameras_status = []
    for cam_dir in list(recordings_path.glob("camera_*")) + list(recordings_path.glob("cam_*")):
        if not cam_dir.is_dir():
            continue
        
        try:
            camera_id = int(cam_dir.name.split("_")[1])
        except (IndexError, ValueError):
            continue
        
        dates = sorted([d.name for d in cam_dir.iterdir() if d.is_dir()])
        if dates:
            total_size = sum(
                f.stat().st_size 
                for date_dir in cam_dir.iterdir() 
                if date_dir.is_dir()
                for f in date_dir.glob("*.mp4")
            )
            
            cameras_status.append({
                "camera_id": camera_id,
                "oldest_date": dates[0] if dates else None,
                "newest_date": dates[-1] if dates else None,
                "total_days": len(dates),
                "total_size_gb": round(total_size / (1024**3), 2)
            })
    
    return {"cameras": cameras_status}

@app.get("/download/{camera_id}/{date}/{filename}")
async def download_segment(camera_id: int, date: str, filename: str):
    """Serve arquivo MP4 com range support para fast start"""
    file_path = Path(f"/recordings/camera_{camera_id}/{date}/{filename}.mp4")
    if not file_path.exists():
        file_path = Path(f"/recordings/cam_{camera_id}/{date}/{filename}.mp4")
    
    if not file_path.exists():
        logger.error(f"Arquivo não encontrado: camera_{camera_id}/{date}/{filename}.mp4")
        raise HTTPException(404, f"Arquivo não encontrado: {filename}.mp4")
    
    logger.info(f"Servindo arquivo: {file_path}")
    return FileResponse(
        file_path, 
        media_type="video/mp4",
        headers={
            "Accept-Ranges": "bytes",
            "Cache-Control": "public, max-age=3600"
        }
    )
