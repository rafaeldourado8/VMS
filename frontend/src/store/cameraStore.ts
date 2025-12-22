import { create } from 'zustand'
import type { Camera } from '@/types'

type GridLayout = 1 | 4 | 9 | 16

interface CameraState {
  cameras: Camera[]
  selectedCamera: Camera | null
  gridLayout: GridLayout
  isFullscreen: boolean
  
  setCameras: (cameras: Camera[]) => void
  selectCamera: (camera: Camera | null) => void
  setGridLayout: (layout: GridLayout) => void
  toggleFullscreen: () => void
  updateCameraStatus: (id: number, status: 'online' | 'offline') => void
}

export const useCameraStore = create<CameraState>((set) => ({
  cameras: [],
  selectedCamera: null,
  gridLayout: 4,
  isFullscreen: false,

  setCameras: (cameras) => set({ cameras }),
  
  selectCamera: (camera) => set({ selectedCamera: camera }),
  
  setGridLayout: (layout) => set({ gridLayout: layout }),
  
  toggleFullscreen: () => set((state) => ({ isFullscreen: !state.isFullscreen })),
  
  updateCameraStatus: (id, status) =>
    set((state) => ({
      cameras: state.cameras.map((cam) =>
        cam.id === id ? { ...cam, status } : cam
      ),
    })),
}))
