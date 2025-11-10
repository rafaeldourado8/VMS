// VMS/frontend/src/components/Analytics.tsx
import React, { useState, useEffect } from "react"
import { BarChart3, Camera, Target, Loader2, AlertCircle } from 'lucide-react'
import { api } from "../lib/api"
import toast from "react-hot-toast"

// Interface para os dados de Analytics da API
// Baseado em VMS/backend/apps/analytics/services.py
interface VehicleTypeStat {
  type: string;
  count: number;
  percentage: number;
}

// Stats do dashboard para os cards
interface StatsData {
  total_cameras: number;
  total_detections_today: number;
}

const Analytics: React.FC = () => {
  const [stats, setStats] = useState<StatsData | null>(null)
  const [vehicleTypes, setVehicleTypes] = useState<VehicleTypeStat[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true)
      setError(null)
      try {
        // O backend usa cache
        const statsPromise = api.get("/dashboard/stats/") //
        const vehicleTypesPromise = api.get("/analytics/vehicle-types/") //

        const [statsData, vehicleTypesData] = await Promise.all([statsPromise, vehicleTypesPromise])
        
        setStats(statsData)
        setVehicleTypes(vehicleTypesData.data) // API retorna {"data": [...]}
      } catch (err: any) {
        setError("Falha ao carregar dados analíticos.")
        toast.error("Falha ao carregar dados analíticos.")
        console.error(err)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [])
  
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
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Analíticos</h1>
        <p className="text-gray-500 mt-1">Estatísticas e análises do sistema</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 bg-blue-100 rounded-xl flex items-center justify-center">
              <Target className="w-7 h-7 text-blue-800" />
            </div>
            <div>
              <p className="text-sm text-gray-600 mb-1">Detecções (Hoje)</p>
              <p className="text-3xl font-bold text-gray-900">{stats?.total_detections_today ?? 0}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 bg-emerald-100 rounded-xl flex items-center justify-center">
              <Camera className="w-7 h-7 text-emerald-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600 mb-1">Total de Câmeras</p>
              <p className="text-3xl font-bold text-gray-900">{stats?.total_cameras ?? 0}</p>
            </div>
          </div>
        </div>
      </div>

      <div className="mt-6 bg-white rounded-xl shadow-sm p-6 border border-gray-200">
        <div className="flex items-center gap-3 mb-4">
          <BarChart3 className="w-6 h-6 text-blue-800" />
          <h2 className="text-xl font-semibold text-gray-900">Detecções por Tipo de Veículo</h2>
        </div>
        
        {vehicleTypes.length > 0 ? (
          <div className="space-y-3">
            {vehicleTypes.map((item) => (
              <div key={item.type} className="flex items-center gap-3">
                <span className="text-sm font-medium text-gray-600 w-24 capitalize">{item.type}</span>
                <div className="flex-1 bg-gray-100 rounded-full h-8 relative overflow-hidden">
                  <div 
                    className="bg-blue-800 h-full rounded-full transition-all flex items-center justify-between px-3"
                    style={{ width: `${item.percentage}%` }}
                  >
                    <span className="text-xs font-semibold text-white">{item.count}</span>
                    <span className="text-xs font-semibold text-white">{item.percentage.toFixed(1)}%</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500">
            <BarChart3 className="w-12 h-12 mx-auto mb-3 text-gray-300" />
            <p>Nenhuma detecção encontrada para exibir estatísticas.</p>
          </div>
        )}
      </div>
    </div>
  )
}

export default Analytics