import cv2
import logging
import time
from threading import Thread, Lock
import numpy as np
import subprocess
import os

class FrameExtractor:
    def __init__(self, camera_id: int, source_url: str, fps: int = 3, use_webrtc: bool = True):
        self.camera_id = camera_id
        self.source_url = source_url
        self.fps = fps
        self.frame_interval = 1.0 / fps
        self.use_webrtc = use_webrtc
        
        self.current_frame = None
        self.frame_lock = Lock()
        self.running = False
        self.thread = None
        
        self.logger = logging.getLogger(__name__)
    
    def start(self):
        if self.running:
            return
        
        self.running = True
        self.thread = Thread(target=self._capture_loop, daemon=True)
        self.thread.start()
        self.logger.info(f"Frame extractor started for camera {self.camera_id} (WebRTC: {self.use_webrtc})")
    
    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        self.logger.info(f"Frame extractor stopped for camera {self.camera_id}")
    
    def get_frame(self) -> np.ndarray:
        with self.frame_lock:
            return self.current_frame.copy() if self.current_frame is not None else None
    
    def _capture_loop(self):
        cap = None
        last_frame_time = 0
        
        while self.running:
            try:
                if cap is None or not cap.isOpened():
                    self.logger.info(f"Connecting to camera {self.camera_id}: {self.source_url}")
                    
                    if self.use_webrtc and self.source_url.startswith('http'):
                        # Tenta WebRTC via GStreamer pipeline
                        cap = self._create_webrtc_capture()
                    else:
                        # Fallback para RTSP com timeouts
                        cap = cv2.VideoCapture(self.source_url)
                        cap.set(cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, 5000)
                        cap.set(cv2.CAP_PROP_READ_TIMEOUT_MSEC, 5000)
                        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                    
                    if cap is None or not cap.isOpened():
                        self.logger.error(f"Failed to connect to camera {self.camera_id}")
                        time.sleep(5)
                        continue
                
                ret, frame = cap.read()
                
                if not ret:
                    self.logger.warning(f"Failed to read frame from camera {self.camera_id}")
                    if cap:
                        cap.release()
                    cap = None
                    time.sleep(5)
                    continue
                
                # FPS throttling
                current_time = time.time()
                if current_time - last_frame_time >= self.frame_interval:
                    with self.frame_lock:
                        self.current_frame = frame
                    last_frame_time = current_time
                
                time.sleep(0.01)
                
            except Exception as e:
                self.logger.error(f"Error in capture loop for camera {self.camera_id}: {e}")
                if cap:
                    cap.release()
                    cap = None
                time.sleep(5)
        
        if cap:
            cap.release()
    
    def _create_webrtc_capture(self):
        """
        Cria captura WebRTC usando GStreamer
        MediaMTX suporta WHEP (WebRTC-HTTP Egress Protocol)
        """
        try:
            # Pipeline GStreamer para WebRTC
            # Usa souphttpsrc para fazer request WHEP ao MediaMTX
            gst_pipeline = (
                f"souphttpsrc location={self.source_url} ! "
                "application/x-rtp-stream,encoding-name=H264 ! "
                "rtph264depay ! h264parse ! avdec_h264 ! "
                "videoconvert ! appsink"
            )
            
            cap = cv2.VideoCapture(gst_pipeline, cv2.CAP_GSTREAMER)
            
            if cap.isOpened():
                self.logger.info(f"WebRTC connection established for camera {self.camera_id}")
                return cap
            else:
                self.logger.warning(f"WebRTC failed for camera {self.camera_id}, falling back to RTSP")
                # Fallback para RTSP
                rtsp_url = self.source_url.replace('/whep', '').replace('8889', '8554').replace('http://', 'rtsp://')
                return cv2.VideoCapture(rtsp_url)
                
        except Exception as e:
            self.logger.error(f"Failed to create WebRTC capture: {e}")
            # Fallback para RTSP
            rtsp_url = self.source_url.replace('/whep', '').replace('8889', '8554').replace('http://', 'rtsp://')
            return cv2.VideoCapture(rtsp_url)
