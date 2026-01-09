// frontend/src/hooks/useDynamicMosaic.ts
import { useState, useCallback } from 'react';

interface MosaicSlot {
  position: number;
  cameraId: string | null;
  streamActive: boolean;
}

export function useDynamicMosaic(maxSlots: number = 4) {
  const [slots, setSlots] = useState<MosaicSlot[]>(
    Array.from({ length: maxSlots }, (_, i) => ({
      position: i,
      cameraId: null,
      streamActive: false,
    }))
  );

  const swapCamera = useCallback((position: number, newCameraId: string) => {
    setSlots(prev => {
      const updated = [...prev];
      // Keep stream alive, just swap camera
      updated[position] = {
        ...updated[position],
        cameraId: newCameraId,
        streamActive: true,
      };
      return updated;
    });
  }, []);

  const activateSlot = useCallback((position: number, cameraId: string) => {
    setSlots(prev => {
      const updated = [...prev];
      updated[position] = { position, cameraId, streamActive: true };
      return updated;
    });
  }, []);

  const deactivateSlot = useCallback((position: number) => {
    setSlots(prev => {
      const updated = [...prev];
      updated[position] = { position, cameraId: null, streamActive: false };
      return updated;
    });
  }, []);

  const activeCount = slots.filter(s => s.streamActive).length;

  return { slots, swapCamera, activateSlot, deactivateSlot, activeCount };
}
