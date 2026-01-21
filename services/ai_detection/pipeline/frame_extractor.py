import cv2
import logging
import time
import asyncio
import threading
import aiohttp
import numpy as np
from threading import Lock
from aiortc import RTCPeerConnection, RTCSessionDescription

class FrameExtractor:
    def __init__(self, camera_id: int, source_url: str, fps: int = 5):
        self.camera_id = camera_id
        self.source_url = source_url  # Ex: http://mediamtx:8889/cam1/whep
        self.fps = fps
        self.target_interval = 1.0 / fps
        
        self.current_frame = None
        self.frame_lock = Lock()
        self.running = False
        self.thread = None
        self.loop = None
        self.pc = None
        
        self.logger = logging.getLogger(__name__)

    def start(self):
        if self.running:
            return
        
        self.running = True
        # Inicia o loop asyncio em uma thread separada para não travar o main
        self.thread = threading.Thread(target=self._start_async_loop, daemon=True)
        self.thread.start()
        self.logger.info(f"WHEP Frame extractor started for camera {self.camera_id}")

    def stop(self):
        self.running = False
        if self.loop:
            asyncio.run_coroutine_threadsafe(self._cleanup(), self.loop)
        if self.thread:
            self.thread.join(timeout=2)
        self.logger.info(f"Frame extractor stopped for camera {self.camera_id}")

    def get_frame(self) -> np.ndarray:
        with self.frame_lock:
            if self.current_frame is not None:
                return self.current_frame.copy()
            return None

    def _start_async_loop(self):
        """Cria e roda o loop de eventos asyncio nesta thread."""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self._consume_webrtc())

    async def _consume_webrtc(self):
        """Gerencia a conexão WHEP e o consumo do stream."""
        self.pc = RTCPeerConnection()
        
        # Prepara para receber vídeo (recvonly)
        self.pc.addTransceiver("video", direction="recvonly")

        @self.pc.on("track")
        def on_track(track):
            self.logger.info(f"Track received for camera {self.camera_id}: {track.kind}")
            if track.kind == "video":
                asyncio.ensure_future(self._read_track(track))

        # 1. Cria oferta SDP (Offer)
        offer = await self.pc.createOffer()
        await self.pc.setLocalDescription(offer)

        # 2. Envia oferta para o MediaMTX (WHEP Handshake)
        try:
            async with aiohttp.ClientSession() as session:
                # O MediaMTX espera o SDP no corpo do POST
                headers = {"Content-Type": "application/sdp"}
                async with session.post(self.source_url, data=self.pc.localDescription.sdp, headers=headers) as resp:
                    if resp.status != 201: # 201 Created é o sucesso do WHEP
                        self.logger.error(f"WHEP Handshake failed: {resp.status} - {await resp.text()}")
                        return
                    
                    # 3. Recebe a resposta SDP (Answer)
                    answer_sdp = await resp.text()
            
            # 4. Configura a resposta remota
            answer = RTCSessionDescription(sdp=answer_sdp, type="answer")
            await self.pc.setRemoteDescription(answer)
            self.logger.info(f"WebRTC connection established for camera {self.camera_id}")

            # Mantém o loop vivo enquanto estiver rodando
            while self.running:
                await asyncio.sleep(1)

        except Exception as e:
            self.logger.error(f"Error in WebRTC connection: {e}")
            self.running = False

    async def _read_track(self, track):
        """Lê frames do track WebRTC continuamente."""
        last_time = time.time()
        
        while self.running:
            try:
                # Recebe o frame (aiortc retorna um objeto VideoFrame)
                frame = await track.recv()
                
                # Controle de FPS simples (descarta frames se estiver muito rápido)
                now = time.time()
                if (now - last_time) < self.target_interval:
                    continue
                last_time = now

                # Converte para array numpy (formato OpenCV BGR)
                # O aiortc usa pyav por baixo dos panos
                img = frame.to_ndarray(format="bgr24")
                
                with self.frame_lock:
                    self.current_frame = img
                    
            except Exception as e:
                self.logger.warning(f"Error reading frame: {e}")
                break

    async def _cleanup(self):
        """Fecha conexões WebRTC."""
        if self.pc:
            await self.pc.close()