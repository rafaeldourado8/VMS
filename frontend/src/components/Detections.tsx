// VMS/frontend/src/components/Detections.tsx
import React, { useState, useEffect } from "react"
import { Target, Camera, Clock, Loader2, AlertCircle } from 'lucide-react'
import { api } from "../lib/api"
import toast from "react-hot-toast"

// Interface para os dados da Detecção da API
// Baseado em VMS/backend/apps/deteccoes/serializers.py
interface DetectionData {
  id: number;
  plate: string | null;
  camera_name: string;
  timestamp: string;
  vehicle_type: string;
  confidence: number | null;
  image_url: string | null;
}

const Detections: React.FC = () => {
  const [detections, setDetections] = useState<DetectionData[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchDetections = async () => {
      setLoading(true)
      setError(null)
      try {
        // O endpoint é /api/detections/
        const data: DetectionData[] = await api.get("/detections/")
        setDetections(data)
      } catch (err: any) {
        setError("Falha ao carregar detecções.")
        toast.error("Falha ao carregar detecções.")
        console.error(err)
      } finally {
        setLoading(false)
      }
    }

    fetchDetections()
  }, [])


  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleString("pt-BR", {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit"
    })
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
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Detecções</h1>
        <p className="text-gray-500 mt-1">Histórico de detecções de veículos</p>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-200">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="px-6 py-4 text-left text-xs font-medium text-gray-600 uppercase">Placa</th>
                <th className="px-6 py-4 text-left text-xs font-medium text-gray-600 uppercase">Câmera</th>
                <th className="px-6 py-4 text-left text-xs font-medium text-gray-600 uppercase">Tipo</th>
                <th className="px-6 py-4 text-left text-xs font-medium text-gray-600 uppercase">Data/Hora</th>
                <th className="px-6 py-4 text-left text-xs font-medium text-gray-600 uppercase">Confiança</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {detections.length > 0 ? (
                detections.map((detection) => (
                  <tr key={detection.id} className="hover:bg-gray-50 transition-colors">
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2">
                        <Target className="w-4 h-4 text-blue-800" />
                        <span className="text-sm font-medium text-gray-900">{detection.plate || "N/A"}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2">
                        <Camera className="w-4 h-4 text-gray-400" />
                        <span className="text-sm text-gray-600">{detection.camera_name}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <span className="inline-flex px-3 py-1 text-xs font-medium bg-gray-100 text-gray-700 rounded-full capitalize">
                        {detection.vehicle_type}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2">
                        <Clock className="w-4 h-4 text-gray-400" />
                        <span className="text-sm text-gray-600">{formatDate(detection.timestamp)}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-600">
                      {detection.confidence ? `${(detection.confidence * 100).toFixed(0)}%` : "N/A"}
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={5} className="text-center py-16 text-gray-500">
                    <Target className="w-16 h-16 mx-auto mb-4 text-gray-300" />
                    <h3 className="text-lg font-semibold">Nenhuma detecção encontrada</h3>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

export default Detections