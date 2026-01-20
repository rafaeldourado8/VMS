import asyncio
import logging
from collections import deque
from typing import Optional
import numpy as np

class FrameBuffer:
    def __init__(self, maxsize: int = 10):
        self.maxsize = maxsize
        self.queue = deque(maxlen=maxsize)
        self.lock = asyncio.Lock()
        self.logger = logging.getLogger(__name__)
    
    async def put(self, frame: np.ndarray):
        async with self.lock:
            if len(self.queue) >= self.maxsize:
                self.queue.popleft()
            self.queue.append(frame)
    
    async def get(self) -> Optional[np.ndarray]:
        async with self.lock:
            if self.queue:
                return self.queue.popleft()
            return None
    
    async def size(self) -> int:
        async with self.lock:
            return len(self.queue)
    
    async def clear(self):
        async with self.lock:
            self.queue.clear()
