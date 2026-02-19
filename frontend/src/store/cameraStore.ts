import { create } from 'zustand'
import type { Camera } from '@/types'
import { clearSnapshotByCamera, clearAllSnapshots } from '@/lib/snapshotCache'

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
  removeCamera: (id: number) => void
  clearAllCameraCache: () => void
}

export const useCameraStore = create<CameraState>((set, get) => ({
  cameras: [],
  selectedCamera: null,
  gridLayout: 4,
  isFullscreen: false,

  setCameras: (cameras) => {
    const oldCameras = get().cameras
    const oldIds = new Set(oldCameras.map(c => c.id))
    const newIds = new Set(cameras.map(c => c.id))
    
    // Limpar cache de câmeras removidas
    oldIds.forEach(id => {
      if (!newIds.has(id)) {
        clearSnapshotByCamera(id)
      }
    })
    
    set({ cameras })
  },
  
  selectCamera: (camera) => set({ selectedCamera: camera }),
  
  setGridLayout: (layout) => set({ gridLayout: layout }),
  
  toggleFullscreen: () => set((state) => ({ isFullscreen: !state.isFullscreen })),
  
  updateCameraStatus: (id, status) =>
    set((state) => ({
      cameras: state.cameras.map((cam) =>
        cam.id === id ? { ...cam, status } : cam
      ),
    })),
  
  removeCamera: (id) => {
    clearSnapshotByCamera(id)
    set((state) => ({
      cameras: state.cameras.filter(cam => cam.id !== id),
      selectedCamera: state.selectedCamera?.id === id ? null : state.selectedCamera
    }))
  },
  
  clearAllCameraCache: () => {
    clearAllSnapshots()
  }
}))