import { useState } from 'react'
import { MapPin, MoreVertical, Maximize2, Settings, Trash2 } from 'lucide-react'
import type { Camera } from '@/types'
import { cn } from '@/lib/utils'
import { Button, Badge } from '@/components/ui'
import { StreamThumbnail } from './StreamThumbnail'
import { streamingService } from '@/services/api'

interface CameraCardProps {
  camera: Camera
  onClick?: () => void
  onDelete?: () => void
  onSettings?: () => void
  compact?: boolean
}

export function CameraCard({
  camera,
  onClick,
  onDelete,
  onSettings,
  compact = false,
}: CameraCardProps) {
  const [menuOpen, setMenuOpen] = useState(false)
  const [isHovered, setIsHovered] = useState(false)

  const hlsUrl = streamingService.getHlsUrl(camera.id)
  const isOnline = camera.status === 'online'

  return (
    <div
      className={cn(
        "relative rounded-xl border border-border bg-card overflow-hidden transition-all",
        isHovered && "ring-2 ring-primary/50",
        onClick && "cursor-pointer"
      )}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => {
        setIsHovered(false)
        setMenuOpen(false)
      }}
      onClick={onClick}
    >
      {/* Video */}
      <div className={cn("relative", compact ? "aspect-video" : "aspect-video")}>
        <StreamThumbnail
          src={hlsUrl}
          fallbackSrc={camera.thumbnail_url || undefined}
          className="w-full h-full"
          onClick={onClick}
          showStatus={false}
        />

        {/* Status badge */}
        <div className="absolute top-3 left-3">
          <Badge variant={isOnline ? "success" : "destructive"}>
            <span className={cn(
              "w-1.5 h-1.5 rounded-full mr-1.5",
              isOnline ? "bg-emerald-400" : "bg-red-400"
            )} />
            {isOnline ? 'Online' : 'Offline'}
          </Badge>
        </div>

        {/* Hover actions */}
        {isHovered && (
          <div className="absolute top-3 right-3 flex gap-1">
            <Button
              variant="secondary"
              size="icon"
              className="h-8 w-8 bg-black/50 hover:bg-black/70"
              onClick={(e) => {
                e.stopPropagation()
                onClick?.()
              }}
            >
              <Maximize2 className="w-4 h-4" />
            </Button>

            <div className="relative">
              <Button
                variant="secondary"
                size="icon"
                className="h-8 w-8 bg-black/50 hover:bg-black/70"
                onClick={(e) => {
                  e.stopPropagation()
                  setMenuOpen(!menuOpen)
                }}
              >
                <MoreVertical className="w-4 h-4" />
              </Button>

              {menuOpen && (
                <div className="absolute right-0 mt-1 w-40 rounded-lg bg-card border border-border shadow-lg z-10">
                  <div className="p-1">
                    <button
                      className="flex w-full items-center gap-2 px-3 py-2 text-sm hover:bg-secondary rounded-md"
                      onClick={(e) => {
                        e.stopPropagation()
                        onSettings?.()
                        setMenuOpen(false)
                      }}
                    >
                      <Settings className="w-4 h-4" />
                      Configurações
                    </button>
                    <button
                      className="flex w-full items-center gap-2 px-3 py-2 text-sm text-destructive hover:bg-secondary rounded-md"
                      onClick={(e) => {
                        e.stopPropagation()
                        onDelete?.()
                        setMenuOpen(false)
                      }}
                    >
                      <Trash2 className="w-4 h-4" />
                      Remover
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Info */}
      {!compact && (
        <div className="p-4">
          <h3 className="font-medium text-sm truncate">{camera.name}</h3>
          {camera.location && (
            <p className="flex items-center gap-1 mt-1 text-xs text-muted-foreground">
              <MapPin className="w-3 h-3" />
              {camera.location}
            </p>
          )}
        </div>
      )}
    </div>
  )
}
