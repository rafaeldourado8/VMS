import { useState, useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Calendar, Clock, Play, ChevronLeft, ChevronRight } from 'lucide-react'
import { Button, Card, CardContent, Input } from '@/components/ui'
import { recordingService } from '@/services/api'
import { VideoPlayer } from './VideoPlayer'

interface RecordingPlayerProps {
  cameraId: number
  cameraName: string
}

export function RecordingPlayer({ cameraId, cameraName }: RecordingPlayerProps) {
  const [selectedDate, setSelectedDate] = useState(
    new Date().toISOString().split('T')[0]
  )
  const [startTime, setStartTime] = useState('')
  const [endTime, setEndTime] = useState('')
  const [playbackUrl, setPlaybackUrl] = useState<string | null>(null)

  const { data: recordings, isLoading } = useQuery({
    queryKey: ['recordings', cameraId, selectedDate, startTime, endTime],
    queryFn: () =>
      recordingService.list({
        camera_id: cameraId,
        date: selectedDate,
        start_time: startTime || undefined,
        end_time: endTime || undefined,
      }),
    enabled: !!selectedDate,
  })

  const handlePlayRecording = (filename: string) => {
    const url = recordingService.getPlaybackUrl(cameraId, selectedDate, filename)
    setPlaybackUrl(url)
  }

  const goToPreviousDay = () => {
    const date = new Date(selectedDate)
    date.setDate(date.getDate() - 1)
    setSelectedDate(date.toISOString().split('T')[0])
    setPlaybackUrl(null)
  }

  const goToNextDay = () => {
    const date = new Date(selectedDate)
    date.setDate(date.getDate() + 1)
    const today = new Date().toISOString().split('T')[0]
    if (date.toISOString().split('T')[0] <= today) {
      setSelectedDate(date.toISOString().split('T')[0])
      setPlaybackUrl(null)
    }
  }

  return (
    <div className="space-y-4">
      <Card>
        <CardContent className="p-4">
          <h3 className="font-medium mb-3">Gravações - {cameraName}</h3>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-3 mb-4">
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="icon"
                onClick={goToPreviousDay}
              >
                <ChevronLeft className="w-4 h-4" />
              </Button>
              <div className="flex-1">
                <Input
                  type="date"
                  value={selectedDate}
                  max={new Date().toISOString().split('T')[0]}
                  onChange={(e) => {
                    setSelectedDate(e.target.value)
                    setPlaybackUrl(null)
                  }}
                />
              </div>
              <Button
                variant="outline"
                size="icon"
                onClick={goToNextDay}
                disabled={selectedDate === new Date().toISOString().split('T')[0]}
              >
                <ChevronRight className="w-4 h-4" />
              </Button>
            </div>

            <Input
              type="time"
              placeholder="Início"
              value={startTime}
              onChange={(e) => setStartTime(e.target.value)}
            />

            <Input
              type="time"
              placeholder="Fim"
              value={endTime}
              onChange={(e) => setEndTime(e.target.value)}
            />

            <Button
              variant="outline"
              onClick={() => {
                setStartTime('')
                setEndTime('')
              }}
            >
              Limpar
            </Button>
          </div>

          {isLoading ? (
            <p className="text-sm text-muted-foreground">Carregando...</p>
          ) : recordings?.recordings.length > 0 ? (
            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm text-muted-foreground mb-2">
                <span>{recordings.recordings.length} gravações</span>
                <span>{recordings.total_size_mb} MB</span>
              </div>

              <div className="max-h-64 overflow-y-auto space-y-1">
                {recordings.recordings.map((rec: any) => (
                  <div
                    key={rec.filename}
                    className="flex items-center justify-between p-2 rounded hover:bg-secondary cursor-pointer"
                    onClick={() => handlePlayRecording(rec.filename)}
                  >
                    <div className="flex items-center gap-2">
                      <Clock className="w-4 h-4 text-muted-foreground" />
                      <span className="font-mono text-sm">{rec.start_time}</span>
                    </div>
                    <div className="flex items-center gap-3">
                      <span className="text-xs text-muted-foreground">
                        {rec.size_mb} MB
                      </span>
                      <Play className="w-4 h-4" />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="text-center py-8">
              <Calendar className="w-12 h-12 mx-auto text-muted-foreground mb-2" />
              <p className="text-sm text-muted-foreground">
                Nenhuma gravação encontrada para esta data
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      {playbackUrl && (
        <Card>
          <CardContent className="p-0">
            <VideoPlayer src={playbackUrl} />
          </CardContent>
        </Card>
      )}
    </div>
  )
}
