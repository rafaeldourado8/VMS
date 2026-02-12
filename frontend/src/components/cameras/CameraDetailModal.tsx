import { useState } from 'react'
import { X } from 'lucide-react'
import { Button } from '@/components/ui'
import { VideoPlayer } from './VideoPlayer'
import { streamingService } from '@/services/api'
import type { Camera } from '@/types'

interface CameraDetailModalProps {
  camera: Camera
  onClose: () => void
}

export function CameraDetailModal({ camera, onClose }: CameraDetailModalProps) {
  const [videoSrc] = useState(streamingService.getHlsUrl(camera.id))

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50">
      <div className="absolute inset-0 bg-black/80" onClick={onClose} />
      <div className="relative w-full max-w-5xl bg-white dark:bg-gray-900 rounded-xl overflow-hidden animate-slide-in shadow-2xl">
        <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900">
          <div>
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white">{camera.name}</h2>
            {camera.location && (
              <p className="text-sm text-gray-600 dark:text-gray-400">{camera.location}</p>
            )}
          </div>
          <div className="flex items-center gap-2">
            <Button variant="ghost" size="icon" onClick={onClose} className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200">
              <X className="w-5 h-5" />
            </Button>
          </div>
        </div>

        <div className="relative aspect-video bg-black">
          <VideoPlayer
            src={videoSrc}
            autoPlay
            muted={false}
            showRecordingControls={true}
            cameraId={camera.id}
            className="h-full"
          />
        </div>

        <div className="p-4 grid grid-cols-2 sm:grid-cols-4 gap-4 text-sm bg-white dark:bg-gray-900">
          <div>
            <p className="text-gray-600 dark:text-gray-400">Status</p>
            <p className="font-medium capitalize text-gray-900 dark:text-white">{camera.status}</p>
          </div>
          <div>
            <p className="text-gray-600 dark:text-gray-400">ID</p>
            <p className="font-medium font-mono text-gray-900 dark:text-white">{camera.id}</p>
          </div>
          <div>
            <p className="text-gray-600 dark:text-gray-400">Criada em</p>
            <p className="font-medium text-gray-900 dark:text-white">
              {new Date(camera.created_at).toLocaleDateString('pt-BR')}
            </p>
          </div>
          <div>
            <p className="text-gray-600 dark:text-gray-400">Stream</p>
            <p className="font-medium font-mono text-xs truncate text-gray-900 dark:text-white">
              cam_{camera.id}
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
