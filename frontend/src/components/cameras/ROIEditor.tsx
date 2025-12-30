import { useState, useRef, useCallback, useEffect } from 'react'
import { Button } from '@/components/ui'
import { Square, Minus, Target, Save, X, Trash2, Palette } from 'lucide-react'
import type { ROIArea, VirtualLine, ZoneTrigger } from '@/types'

interface ROIEditorProps {
  videoSrc: string
  onSave: (config: {
    roi_areas: ROIArea[]
    virtual_lines: VirtualLine[]
    tripwires: VirtualLine[]
    zone_triggers: ZoneTrigger[]
  }) => void
  onClose: () => void
  initialConfig?: {
    roi_areas?: ROIArea[]
    virtual_lines?: VirtualLine[]
    tripwires?: VirtualLine[]
    zone_triggers?: ZoneTrigger[]
  }
}

type DrawMode = 'roi' | 'line' | 'tripwire' | 'zone' | 'delete' | null

const COLORS = {
  roi: '#00ff00',
  line: '#0066ff', 
  tripwire: '#ff0000',
  zone: '#ffff00',
  selected: '#ff00ff'
}

export function ROIEditor({ videoSrc, onSave, onClose, initialConfig }: ROIEditorProps) {
  const videoRef = useRef<HTMLVideoElement>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const [drawMode, setDrawMode] = useState<DrawMode>(null)
  const [isDrawing, setIsDrawing] = useState(false)
  const [currentPoints, setCurrentPoints] = useState<{ x: number; y: number }[]>([])
  const [selectedColor, setSelectedColor] = useState('#00ff00')
  const [selectedElement, setSelectedElement] = useState<{type: string, id: string} | null>(null)
  
  const [roiAreas, setRoiAreas] = useState<ROIArea[]>(initialConfig?.roi_areas || [])
  const [virtualLines, setVirtualLines] = useState<VirtualLine[]>(initialConfig?.virtual_lines || [])
  const [tripwires, setTripwires] = useState<VirtualLine[]>(initialConfig?.tripwires || [])
  const [zoneTriggers, setZoneTriggers] = useState<ZoneTrigger[]>(initialConfig?.zone_triggers || [])

  const drawOverlay = useCallback(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    
    const ctx = canvas.getContext('2d')
    if (!ctx) return
    
    ctx.clearRect(0, 0, canvas.width, canvas.height)
    
    // Draw ROI areas
    roiAreas.forEach(roi => {
      ctx.strokeStyle = roi.color || COLORS.roi
      ctx.fillStyle = roi.color ? roi.color + '33' : 'rgba(0, 255, 0, 0.2)'
      ctx.lineWidth = 2
      ctx.beginPath()
      roi.points.forEach((point, i) => {
        const x = point.x * canvas.width
        const y = point.y * canvas.height
        if (i === 0) ctx.moveTo(x, y)
        else ctx.lineTo(x, y)
      })
      ctx.closePath()
      ctx.fill()
      ctx.stroke()
    })
    
    // Draw virtual lines
    virtualLines.forEach(line => {
      ctx.strokeStyle = line.color || COLORS.line
      ctx.lineWidth = 3
      ctx.beginPath()
      ctx.moveTo(line.start.x * canvas.width, line.start.y * canvas.height)
      ctx.lineTo(line.end.x * canvas.width, line.end.y * canvas.height)
      ctx.stroke()
    })
    
    // Draw tripwires
    tripwires.forEach(tripwire => {
      ctx.strokeStyle = tripwire.color || COLORS.tripwire
      ctx.lineWidth = 4
      ctx.setLineDash([10, 5])
      ctx.beginPath()
      ctx.moveTo(tripwire.start.x * canvas.width, tripwire.start.y * canvas.height)
      ctx.lineTo(tripwire.end.x * canvas.width, tripwire.end.y * canvas.height)
      ctx.stroke()
      ctx.setLineDash([])
    })
    
    // Draw zone triggers
    zoneTriggers.forEach(zone => {
      ctx.strokeStyle = zone.color || COLORS.zone
      ctx.fillStyle = zone.color ? zone.color + '33' : 'rgba(255, 255, 0, 0.2)'
      ctx.lineWidth = 2
      ctx.beginPath()
      zone.points.forEach((point, i) => {
        const x = point.x * canvas.width
        const y = point.y * canvas.height
        if (i === 0) ctx.moveTo(x, y)
        else ctx.lineTo(x, y)
      })
      ctx.closePath()
      ctx.fill()
      ctx.stroke()
    })
    
    // Draw current drawing
    if (isDrawing && currentPoints.length > 0 && drawMode !== 'line') {
      ctx.strokeStyle = selectedColor
      ctx.lineWidth = 2
      ctx.setLineDash([5, 5])
      ctx.beginPath()
      currentPoints.forEach((point, i) => {
        const x = point.x * canvas.width
        const y = point.y * canvas.height
        if (i === 0) ctx.moveTo(x, y)
        else ctx.lineTo(x, y)
      })
      ctx.stroke()
      ctx.setLineDash([])
      
      // Draw points
      currentPoints.forEach(point => {
        ctx.fillStyle = selectedColor
        ctx.beginPath()
        ctx.arc(point.x * canvas.width, point.y * canvas.height, 4, 0, 2 * Math.PI)
        ctx.fill()
      })
    }
  }, [roiAreas, virtualLines, tripwires, zoneTriggers, currentPoints, isDrawing, selectedColor, drawMode])

  // Redraw overlay when elements change
  useEffect(() => {
    drawOverlay()
  }, [roiAreas, virtualLines, tripwires, zoneTriggers, drawOverlay])

  const getRelativeCoords = useCallback((e: React.MouseEvent) => {
    const canvas = canvasRef.current
    if (!canvas) return { x: 0, y: 0 }
    
    const rect = canvas.getBoundingClientRect()
    return {
      x: (e.clientX - rect.left) / rect.width,
      y: (e.clientY - rect.top) / rect.height
    }
  }, [])

  const isPointInPolygon = (point: {x: number, y: number}, polygon: {x: number, y: number}[]) => {
    let inside = false
    for (let i = 0, j = polygon.length - 1; i < polygon.length; j = i++) {
      if (((polygon[i].y > point.y) !== (polygon[j].y > point.y)) &&
          (point.x < (polygon[j].x - polygon[i].x) * (point.y - polygon[i].y) / (polygon[j].y - polygon[i].y) + polygon[i].x)) {
        inside = !inside
      }
    }
    return inside
  }

  const isPointOnLine = (point: {x: number, y: number}, line: VirtualLine, tolerance = 0.02) => {
    const d = Math.sqrt(Math.pow(line.end.x - line.start.x, 2) + Math.pow(line.end.y - line.start.y, 2))
    const t = ((point.x - line.start.x) * (line.end.x - line.start.x) + (point.y - line.start.y) * (line.end.y - line.start.y)) / (d * d)
    if (t < 0 || t > 1) return false
    const projection = {
      x: line.start.x + t * (line.end.x - line.start.x),
      y: line.start.y + t * (line.end.y - line.start.y)
    }
    const distance = Math.sqrt(Math.pow(point.x - projection.x, 2) + Math.pow(point.y - projection.y, 2))
    return distance < tolerance
  }

  const handleCanvasMouseDown = useCallback((e: React.MouseEvent) => {
    const coords = getRelativeCoords(e)
    
    if (drawMode === 'delete') {
      // Check for elements to delete
      for (const roi of roiAreas) {
        if (isPointInPolygon(coords, roi.points)) {
          setRoiAreas(prev => prev.filter(r => r.id !== roi.id))
          return
        }
      }
      for (const line of virtualLines) {
        if (isPointOnLine(coords, line)) {
          setVirtualLines(prev => prev.filter(l => l.id !== line.id))
          return
        }
      }
      for (const tripwire of tripwires) {
        if (isPointOnLine(coords, tripwire)) {
          setTripwires(prev => prev.filter(t => t.id !== tripwire.id))
          return
        }
      }
      for (const zone of zoneTriggers) {
        if (isPointInPolygon(coords, zone.points)) {
          setZoneTriggers(prev => prev.filter(z => z.id !== zone.id))
          return
        }
      }
      return
    }
    
    if (!drawMode) return
    
    if (drawMode === 'line' || drawMode === 'tripwire') {
      if (currentPoints.length === 0) {
        setCurrentPoints([coords])
        setIsDrawing(true)
      } else {
        if (drawMode === 'line') {
          const newLine: VirtualLine = {
            id: Date.now().toString(),
            name: `Linha ${virtualLines.length + 1}`,
            start: currentPoints[0],
            end: coords,
            direction: 'both',
            enabled: true,
            color: selectedColor
          }
          setVirtualLines(prev => [...prev, newLine])
        } else {
          const newTripwire: VirtualLine = {
            id: Date.now().toString(),
            name: `Tripwire ${tripwires.length + 1}`,
            start: currentPoints[0],
            end: coords,
            direction: 'both',
            enabled: true,
            color: selectedColor
          }
          setTripwires(prev => [...prev, newTripwire])
        }
        setCurrentPoints([])
        setIsDrawing(false)
      }
    } else if (drawMode === 'roi' || drawMode === 'zone') {
      setCurrentPoints(prev => [...prev, coords])
      setIsDrawing(true)
    }
  }, [drawMode, currentPoints, roiAreas, virtualLines, tripwires, zoneTriggers, selectedColor, getRelativeCoords])

  const handleCanvasDoubleClick = useCallback((e: React.MouseEvent) => {
    if (!drawMode || drawMode === 'line' || drawMode === 'tripwire' || drawMode === 'delete') return
    
    if (currentPoints.length >= 3) {
      if (drawMode === 'roi') {
        const newROI: ROIArea = {
          id: Date.now().toString(),
          name: `ROI ${roiAreas.length + 1}`,
          points: currentPoints,
          enabled: true,
          color: selectedColor
        }
        setRoiAreas(prev => [...prev, newROI])
      } else if (drawMode === 'zone') {
        const newZone: ZoneTrigger = {
          id: Date.now().toString(),
          name: `Zona ${zoneTriggers.length + 1}`,
          points: currentPoints,
          triggerType: 'both',
          enabled: true,
          color: selectedColor
        }
        setZoneTriggers(prev => [...prev, newZone])
      }
    }
    setCurrentPoints([])
    setIsDrawing(false)
  }, [drawMode, currentPoints, roiAreas.length, zoneTriggers.length, selectedColor])

  const handleCanvasMouseMove = useCallback((e: React.MouseEvent) => {
    if (!isDrawing) return
    
    const coords = getRelativeCoords(e)
    
    if (drawMode === 'line' && currentPoints.length === 1) {
      // Update preview for line drawing
      const canvas = canvasRef.current
      if (!canvas) return
      
      const ctx = canvas.getContext('2d')
      if (!ctx) return
      
      // Redraw everything
      drawOverlay()
      
      // Draw preview line
      ctx.strokeStyle = selectedColor
      ctx.lineWidth = 3
      ctx.setLineDash([5, 5])
      ctx.beginPath()
      ctx.moveTo(currentPoints[0].x * canvas.width, currentPoints[0].y * canvas.height)
      ctx.lineTo(coords.x * canvas.width, coords.y * canvas.height)
      ctx.stroke()
      ctx.setLineDash([])
    }
    
    if (drawMode === 'tripwire' && currentPoints.length === 1) {
      // Update preview for tripwire drawing
      const canvas = canvasRef.current
      if (!canvas) return
      
      const ctx = canvas.getContext('2d')
      if (!ctx) return
      
      // Redraw everything
      drawOverlay()
      
      // Draw preview tripwire
      ctx.strokeStyle = selectedColor
      ctx.lineWidth = 4
      ctx.setLineDash([10, 5])
      ctx.beginPath()
      ctx.moveTo(currentPoints[0].x * canvas.width, currentPoints[0].y * canvas.height)
      ctx.lineTo(coords.x * canvas.width, coords.y * canvas.height)
      ctx.stroke()
      ctx.setLineDash([])
    }
  }, [isDrawing, drawMode, currentPoints, selectedColor, getRelativeCoords, drawOverlay])

  const clearAll = () => {
    if (confirm('Apagar todas as configurações?')) {
      setRoiAreas([])
      setVirtualLines([])
      setTripwires([])
      setZoneTriggers([])
      setCurrentPoints([])
      setIsDrawing(false)
    }
  }

  const handleSave = () => {
    onSave({
      roi_areas: roiAreas,
      virtual_lines: virtualLines,
      tripwires: tripwires,
      zone_triggers: zoneTriggers
    })
  }

  return (
    <div className="fixed inset-0 z-50 bg-black/90 flex flex-col">
      <div className="flex items-center justify-between p-4 bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-700">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Configurar Detecção</h2>
        <div className="flex gap-2">
          <Button
            variant={drawMode === 'roi' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setDrawMode(drawMode === 'roi' ? null : 'roi')}
          >
            <Square className="w-4 h-4 mr-2" />
            ROI
          </Button>
          <Button
            variant={drawMode === 'line' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setDrawMode(drawMode === 'line' ? null : 'line')}
          >
            <Minus className="w-4 h-4 mr-2" />
            Linha Virtual
          </Button>
          <Button
            variant={drawMode === 'tripwire' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setDrawMode(drawMode === 'tripwire' ? null : 'tripwire')}
          >
            <Minus className="w-4 h-4 mr-2" />
            Tripwire
          </Button>
          <Button
            variant={drawMode === 'zone' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setDrawMode(drawMode === 'zone' ? null : 'zone')}
          >
            <Target className="w-4 h-4 mr-2" />
            Zona
          </Button>
          <Button
            variant={drawMode === 'delete' ? 'destructive' : 'outline'}
            size="sm"
            onClick={() => setDrawMode(drawMode === 'delete' ? null : 'delete')}
          >
            <Trash2 className="w-4 h-4 mr-2" />
            Apagar
          </Button>
          <div className="flex items-center gap-2">
            <Palette className="w-4 h-4" />
            <input
              type="color"
              value={selectedColor}
              onChange={(e) => setSelectedColor(e.target.value)}
              className="w-8 h-8 rounded border cursor-pointer"
              title="Escolher cor"
            />
          </div>
          <Button variant="outline" onClick={clearAll} size="sm">
            Limpar Tudo
          </Button>
          <Button onClick={handleSave} size="sm">
            <Save className="w-4 h-4 mr-2" />
            Salvar
          </Button>
          <Button variant="outline" onClick={onClose} size="sm">
            <X className="w-4 h-4" />
          </Button>
        </div>
      </div>
      
      <div className="flex-1 flex items-center justify-center p-4">
        <div className="relative max-w-full max-h-full">
          <video
            ref={videoRef}
            src={videoSrc}
            className="max-w-full max-h-full"
            onLoadedMetadata={() => {
              const canvas = canvasRef.current
              const video = videoRef.current
              if (canvas && video) {
                canvas.width = video.videoWidth
                canvas.height = video.videoHeight
                canvas.style.width = `${video.offsetWidth}px`
                canvas.style.height = `${video.offsetHeight}px`
                drawOverlay()
              }
            }}
            controls
          />
          <canvas
            ref={canvasRef}
            className={`absolute inset-0 ${drawMode ? 'cursor-crosshair' : 'cursor-default'}`}
            onMouseDown={handleCanvasMouseDown}
            onDoubleClick={handleCanvasDoubleClick}
            onMouseMove={handleCanvasMouseMove}
          />
        </div>
      </div>
      
      <div className="p-4 bg-white dark:bg-gray-900 text-sm text-gray-600 dark:text-gray-400 border-t border-gray-200 dark:border-gray-700">
        {drawMode === 'roi' && 'Clique para adicionar pontos da área ROI. Duplo clique para finalizar.'}
        {drawMode === 'line' && 'Clique para definir início e fim da linha virtual.'}
        {drawMode === 'tripwire' && 'Clique para definir início e fim do tripwire.'}
        {drawMode === 'zone' && 'Clique para adicionar pontos da zona de trigger. Duplo clique para finalizar.'}
        {drawMode === 'delete' && 'Clique em qualquer elemento para apagá-lo.'}
        {!drawMode && 'Selecione um tipo de detecção para começar a desenhar.'}
      </div>
    </div>
  )
}