import sys
sys.path.insert(0, '/app')

from fastapi import FastAPI, Header, HTTPException
from uuid import UUID
import redis
from shared.streaming import RedisStreamingManager, HTTPMediaMTXAdapter

app = FastAPI(title="VMS Streaming API")

redis_client = redis.Redis(host='redis', port=6379, decode_responses=False)
mediamtx = HTTPMediaMTXAdapter()
streaming_manager = RedisStreamingManager(redis_client, mediamtx)

@app.post("/api/streaming/start/{camera_public_id}")
async def start_stream(
    camera_public_id: UUID,
    x_city_id: UUID = Header(..., alias="X-City-ID"),
    x_user_id: int = Header(..., alias="X-User-ID")
):
    try:
        session = streaming_manager.start_stream(camera_public_id, x_city_id, x_user_id)
        return {
            "session_id": session.session_id,
            "hls_url": mediamtx.get_hls_url(session.session_id),
            "started_at": session.started_at.isoformat()
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/streaming/stop/{session_id}")
async def stop_stream(
    session_id: str,
    x_city_id: UUID = Header(..., alias="X-City-ID")
):
    stopped = streaming_manager.stop_stream(session_id, x_city_id)
    if not stopped:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"status": "stopped"}

@app.get("/api/streaming/sessions")
async def list_sessions(x_city_id: UUID = Header(..., alias="X-City-ID")):
    sessions = streaming_manager.list_active_sessions(x_city_id)
    return {
        "count": len(sessions),
        "sessions": [
            {
                "session_id": s.session_id,
                "camera_id": str(s.camera_id),
                "public_id": str(s.public_id),
                "started_at": s.started_at.isoformat(),
                "protocol": s.protocol
            }
            for s in sessions
        ]
    }

@app.get("/health")
async def health():
    return {"status": "ok"}
