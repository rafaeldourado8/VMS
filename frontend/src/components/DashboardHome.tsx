// VMS/frontend/src/components/DashboardHome.tsx
import React, { useState, useEffect } from "react"
import { Activity, Clock, Camera, AlertCircle, Loader2 } from 'lucide-react'
import { api } from "../lib/api"
import toast from "react-hot-toast"

// Interfaces para os dados da API
interface StatsData {
  total_cameras: number;
  online_cameras: number;
  offline_cameras: number;
  total_detections_today: number;
}

interface RecentEvent {
  id: number;
  plate: string | null;
  camera_name: string;
  timestamp: string;
  vehicle_type: string;
}

const DashboardHome: React.FC = () => {
  const [stats, setStats] = useState<StatsData | null>(null)
  const [events, setEvents] = useState<RecentEvent[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true)
      setError(null)
      try {
        // O backend usa cache, então podemos chamar com segurança
        const statsPromise = api.get("/dashboard/stats/") //
        const eventsPromise = api.get("/dashboard/recent-events/?limit=5") //

        const [statsData, eventsData] = await Promise.all([statsPromise, eventsPromise])
        
        setStats(statsData)
        setEvents(eventsData.events) // O endpoint retorna {"events": [...]}
      } catch (err: any) {
        setError("Falha ao carregar dados do dashboard.")
        toast.error("Falha ao carregar dados do dashboard.")
        console.error(err)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [])

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleString("pt-BR", {
      day: "2-digit",
      month: "2-digit",
      hour: "2-digit",
      minute: "2-digit"
    })
  }
  
  const getEventDescription = (event: RecentEvent): string => {
    if (event.plate) {
      return `Placa ${event.plate} (${event.vehicle_type}) detectada em ${event.camera_name}`
    }
    return `Detecção (${event.vehicle_type}) em ${event.camera_name}`
  }

  if (loading) {
    return (
      <div className="p-8 flex items-center justify-center h-full">
        <Loader2 className="w-12 h-12 text-blue-800 animate-spin" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="p-8 flex flex-col items-center justify-center h-full text-red-600">
        <AlertCircle className="w-12 h-12 mb-4" />
        <h2 className="text-xl font-semibold">Erro ao carregar</h2>
        <p>{error}</p>
      </div>
    )
  }

  return (
    <div className="p-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-500 mt-1">Visão geral do sistema de monitoramento</p>
      </div>

      {/* Status Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        {/* Câmeras Totais */}
        <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 bg-blue-100 rounded-xl flex items-center justify-center">
              <Camera className="w-7 h-7 text-blue-800" />
            </div>
            <div>
              <p className="text-sm text-gray-600 mb-1">Câmeras Totais</p>
              <p className="text-3xl font-bold text-gray-900">{stats?.total_cameras ?? 0}</p>
            </div>
          </div>
        </div>

        {/* Câmeras Online */}
        <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 bg-emerald-100 rounded-xl flex items-center justify-center">
              <Camera className="w-7 h-7 text-emerald-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600 mb-1">Câmeras Online</p>
              <p className="text-3xl font-bold text-gray-900">{stats?.online_cameras ?? 0}</p>
            </div>
          </div>
        </div>

        {/* Detecções Hoje */}
        <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 bg-orange-100 rounded-xl flex items-center justify-center">
              <Activity className="w-7 h-7 text-orange-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600 mb-1">Detecções (Hoje)</p>
              <p className="text-3xl font-bold text-gray-900">{stats?.total_detections_today ?? 0}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Content Grid */}
      <div className="grid grid-cols-1">
        {/* Recent Events */}
        <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
          <div className="flex items-center gap-3 mb-6">
            <div className="w-10 h-10 bg-orange-100 rounded-lg flex items-center justify-center">
              <Activity className="w-5 h-5 text-orange-600" />
            </div>
            <h2 className="text-xl font-semibold text-gray-900">Eventos Recentes</h2>
          </div>
          
          <div className="space-y-4">
            {events.length > 0 ? (
              events.map((event) => (
                <div key={event.id} className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg">
                  <div className="w-2 h-2 rounded-full mt-2 bg-emerald-500" />
                  <div className="flex-1">
                    <p className="text-sm font-medium text-gray-900">{getEventDescription(event)}</p>
                    <p className="text-xs text-gray-500 mt-1 flex items-center gap-1">
                      <Clock className="w-3 h-3" />
                      {formatDate(event.timestamp)}
                    </p>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center py-8 text-gray-500">
                <Activity className="w-12 h-12 mx-auto mb-3 text-gray-300" />
                <p>Nenhum evento recente</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default DashboardHome