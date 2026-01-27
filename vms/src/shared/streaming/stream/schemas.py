from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import List, Optional

# Streaming
class StreamStartResponse(BaseModel):
    session_id: str
    camera_id: UUID
    hls_url: str
    webrtc_url: Optional[str] = None
    started_at: datetime
    
class StreamStopResponse(BaseModel):
    session_id: str
    stopped_at: datetime
    
class StreamSessionResponse(BaseModel):
    session_id: str
    camera_id: UUID
    public_id: UUID
    protocol: str
    started_at: datetime
    hls_url: str
    
class StreamListResponse(BaseModel):
    count: int
    sessions: List[StreamSessionResponse]

# Recording
class RecordingEnableResponse(BaseModel):
    camera_id: UUID
    recording: bool = True
    storage_path: str
    enabled_at: datetime
    
class RecordingDisableResponse(BaseModel):
    camera_id: UUID
    recording: bool = False
    disabled_at: datetime
    
class RecordingStatusResponse(BaseModel):
    camera_id: UUID
    recording: bool
    storage_path: Optional[str] = None
    started_at: Optional[datetime] = None

# Mosaic
class MosaicCreateResponse(BaseModel):
    mosaic_id: str
    city_id: UUID
    user_id: int
    max_streams: int = 4
    current_streams: int = 0
    
class MosaicResponse(BaseModel):
    mosaic_id: str
    city_id: UUID
    user_id: int
    session_ids: List[str]
    max_streams: int
    current_streams: int
    
class MosaicAddStreamResponse(BaseModel):
    mosaic_id: str
    session_id: str
    added: bool = True
    current_streams: int

class MosaicRemoveStreamResponse(BaseModel):
    mosaic_id: str
    session_id: str
    removed: bool = True
    current_streams: int

class MosaicDeleteResponse(BaseModel):
    mosaic_id: str
    deleted: bool = True

# Health
class HealthResponse(BaseModel):
    status: str
    version: str = "1.0.0"
    mediamtx: bool
    redis: bool
