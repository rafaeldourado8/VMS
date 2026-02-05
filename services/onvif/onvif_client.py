from onvif import ONVIFCamera
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class ONVIFClient:
    def __init__(self, ip: str, port: int, username: str, password: str):
        self.ip = ip
        self.port = port
        self.username = username
        self.password = password
    
    async def get_recordings(self, start_time: datetime, end_time: datetime):
        """Lista gravações disponíveis."""
        try:
            cam = ONVIFCamera(self.ip, self.port, self.username, self.password)
            recording_service = cam.create_recording_service()
            
            recordings = recording_service.GetRecordings()
            
            result = []
            for rec in recordings:
                result.append({
                    'token': rec.RecordingToken,
                    'source': rec.Source.SourceId if hasattr(rec, 'Source') else None,
                    'name': rec.Name if hasattr(rec, 'Name') else None,
                    'earliest': rec.EarliestRecording.isoformat() if hasattr(rec, 'EarliestRecording') else None,
                    'latest': rec.LatestRecording.isoformat() if hasattr(rec, 'LatestRecording') else None
                })
            
            return result
        except Exception as e:
            logger.error(f"ONVIF GetRecordings error: {e}")
            return []
    
    async def get_replay_uri(self, recording_token: str, start_time: datetime):
        """Obtém URI RTSP para replay."""
        try:
            cam = ONVIFCamera(self.ip, self.port, self.username, self.password)
            replay_service = cam.create_replay_service()
            
            stream_setup = {
                'Stream': 'RTP-Unicast',
                'Transport': {
                    'Protocol': 'RTSP'
                }
            }
            
            replay_config = {
                'RecordingToken': recording_token,
                'StreamSetup': stream_setup
            }
            
            replay_uri = replay_service.GetReplayUri(replay_config)
            
            return replay_uri.Uri
        except Exception as e:
            logger.error(f"ONVIF GetReplayUri error: {e}")
            return None
