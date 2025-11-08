"""
Streaming routes
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, List
from pydantic import BaseModel

router = APIRouter()

# In-memory storage
streams_db: Dict[str, dict] = {}


class StreamCreate(BaseModel):
    camera_id: int
    stream_url: str
    protocol: str = "rtsp"


class StreamResponse(BaseModel):
    stream_id: str
    camera_id: int
    stream_url: str
    protocol: str
    status: str


@router.get("/streams/", response_model=List[StreamResponse])
async def list_streams():
    """List all streams."""
    return list(streams_db.values())


@router.post("/streams/", response_model=StreamResponse, status_code=201)
async def create_stream(stream: StreamCreate):
    """Create a new stream."""
    stream_id = f"stream_{stream.camera_id}_{len(streams_db) + 1}"
    
    stream_data = {
        "stream_id": stream_id,
        "camera_id": stream.camera_id,
        "stream_url": stream.stream_url,
        "protocol": stream.protocol,
        "status": "active"
    }
    
    streams_db[stream_id] = stream_data
    return stream_data


@router.get("/streams/{stream_id}", response_model=StreamResponse)
async def get_stream(stream_id: str):
    """Get stream by ID."""
    if stream_id not in streams_db:
        raise HTTPException(status_code=404, detail="Stream not found")
    return streams_db[stream_id]


@router.delete("/streams/{stream_id}")
async def delete_stream(stream_id: str):
    """Delete a stream."""
    if stream_id not in streams_db:
        raise HTTPException(status_code=404, detail="Stream not found")
    
    del streams_db[stream_id]
    return {"detail": "Stream deleted successfully"}


@router.patch("/streams/{stream_id}", response_model=StreamResponse)
async def update_stream(stream_id: str, stream_url: str = None, protocol: str = None):
    """Update a stream."""
    if stream_id not in streams_db:
        raise HTTPException(status_code=404, detail="Stream not found")
    
    if stream_url:
        streams_db[stream_id]["stream_url"] = stream_url
    if protocol:
        streams_db[stream_id]["protocol"] = protocol
    
    return streams_db[stream_id]