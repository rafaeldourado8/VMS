import { useState, useEffect } from 'react';

export const useTimelineState = (currentTime: Date) => {
  const [viewWindow, setViewWindow] = useState({
    start: currentTime.getTime() - 30 * 60 * 1000,
    end: currentTime.getTime() + 30 * 60 * 1000
  });

  const [isDragging, setIsDragging] = useState(false);
  const [lastX, setLastX] = useState(0);
  const [dragStartX, setDragStartX] = useState(0);
  const [autoFollow, setAutoFollow] = useState(true);
  const [hoverTime, setHoverTime] = useState<Date | null>(null);
  const [hoverX, setHoverX] = useState(0);

  useEffect(() => {
    if (!autoFollow) return;
    
    const currentMs = currentTime.getTime();
    const margin = (viewWindow.end - viewWindow.start) * 0.1;
    
    if (currentMs < viewWindow.start + margin || currentMs > viewWindow.end - margin) {
      const range = viewWindow.end - viewWindow.start;
      setViewWindow({
        start: currentMs - range / 2,
        end: currentMs + range / 2
      });
    }
  }, [currentTime, autoFollow]);

  return {
    viewWindow,
    setViewWindow,
    isDragging,
    setIsDragging,
    lastX,
    setLastX,
    dragStartX,
    setDragStartX,
    autoFollow,
    setAutoFollow,
    hoverTime,
    setHoverTime,
    hoverX,
    setHoverX
  };
};
