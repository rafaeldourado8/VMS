import { useEffect, useState } from 'react'
import { Car, Clock, Camera, CheckCircle2 } from 'lucide-react'
import { Card, CardHeader, CardTitle, CardContent, Badge } from '@/components/ui'
import { formatRelativeTime } from '@/lib/utils'

interface Detection {
  id: string
  camera_id: number
  plate: string
  confidence: number
  method: string
  timestamp: string
  metadata: {
    track_id: number
    frames_analyzed: number
    votes: number
    total: number
  }
}

export function LiveDetections() {
  const [detections, setDetections] = useState<Detection[]>([])
  const [isConnected, setIsConnected] = useState(false)

  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8000/ws/detections')

    ws.onopen = () => {
      setIsConnected(true)
    }

    ws.onmessage = (event) => {
      const detection = JSON.parse(event.data)
      setDetections((prev) => [detection, ...prev].slice(0, 20))
    }

    ws.onerror = () => {
      setIsConnected(false)
    }

    ws.onclose = () => {
      setIsConnected(false)
    }

    return () => ws.close()
  }, [])

  const getMethodColor = (method: string) => {
    switch (method) {
      case 'simple_majority':
        return 'bg-emerald-500/10 text-emerald-500'
      case 'similarity_voting':
        return 'bg-blue-500/10 text-blue-500'
      default:
        return 'bg-amber-500/10 text-amber-500'
    }
  }

  const getMethodLabel = (method: string) => {
    switch (method) {
      case 'simple_majority':
        return 'Maioria'
      case 'similarity_voting':
        return 'Similaridade'
      default:
        return 'Confiança'
    }
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="text-base font-medium flex items-center gap-2">
            <Car className="w-4 h-4" />
            Detecções em Tempo Real
          </CardTitle>
          <div className="flex items-center gap-2">
            <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-emerald-500' : 'bg-red-500'} animate-pulse`} />
            <span className="text-xs text-muted-foreground">
              {isConnected ? 'Conectado' : 'Desconectado'}
            </span>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {detections.length === 0 ? (
          <div className="text-center py-12">
            <Car className="w-12 h-12 mx-auto text-muted-foreground/50 mb-3" />
            <p className="text-sm text-muted-foreground">Aguardando detecções...</p>
          </div>
        ) : (
          <div className="space-y-2 max-h-[600px] overflow-y-auto">
            {detections.map((detection) => (
              <div key={detection.id} className="flex items-center gap-3 p-3 rounded-lg border border-border hover:bg-secondary/50 transition-colors">
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <span className="text-lg font-mono font-bold">{detection.plate}</span>
                    <Badge variant="secondary" className={getMethodColor(detection.method)}>
                      {getMethodLabel(detection.method)}
                    </Badge>
                  </div>
                  <div className="flex items-center gap-3 mt-1 text-xs text-muted-foreground">
                    <span className="flex items-center gap-1">
                      <Camera className="w-3 h-3" />
                      Câmera {detection.camera_id}
                    </span>
                    <span className="flex items-center gap-1">
                      <CheckCircle2 className="w-3 h-3" />
                      {detection.metadata.votes}/{detection.metadata.total} votos
                    </span>
                    <span>{detection.metadata.frames_analyzed} frames</span>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-sm font-medium">{(detection.confidence * 100).toFixed(0)}%</div>
                  <div className="text-xs text-muted-foreground flex items-center gap-1">
                    <Clock className="w-3 h-3" />
                    {formatRelativeTime(detection.timestamp)}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
