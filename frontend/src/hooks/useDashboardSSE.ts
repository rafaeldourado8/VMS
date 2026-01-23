import { useEffect, useState } from 'react'

interface DashboardStats {
  total_cameras: number
  cameras_status: {
    online: number
    offline: number
  }
  detections_24h: number
  detections_by_type: Record<string, number>
  recent_activity: Array<{
    id: number
    plate: string
    camera: string
    time: string
  }>
  alerts: number
}

export function useDashboardSSE() {
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [isConnected, setIsConnected] = useState(false)

  useEffect(() => {
    const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'
    const eventSource = new EventSource(`${apiUrl}/api/dashboard/stream`)

    eventSource.onopen = () => {
      setIsConnected(true)
    }

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        setStats(data)
      } catch (error) {
        console.error('Error parsing SSE data:', error)
      }
    }

    eventSource.onerror = () => {
      setIsConnected(false)
      eventSource.close()
    }

    return () => {
      eventSource.close()
    }
  }, [])

  return { stats, isConnected }
}
