// VMS/frontend/src/components/Cameras.tsx
import React, { useState, useEffect } from "react"
import { Camera, Circle, Loader2, AlertCircle } from 'lucide-react'
import { api } from "../lib/api"
import toast from "react-hot-toast"

// Interface para os dados da Câmera da API
// Baseado em VMS/backend/apps/cameras/serializers.py
interface CameraData {
  id: number;
  name: string;
  location: string | null;
  status: "online" | "offline";
  stream_url: string;
  thumbnail_url: string | null;
}

const Cameras: React.FC = () => {
  const [cameras, setCameras] = useState<CameraData[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchCameras = async () => {
      setLoading(true)
      setError(null)
      try {
        // O endpoint é /api/cameras/
        const data: CameraData[] = await api.get("/cameras/")
        setCameras(data)
      } catch (err: any) {
        setError("Falha ao carregar câmeras.")
        toast.error("Falha ao carregar câmeras.")
        console.error(err)
      } finally {
        setLoading(false)
      }
    }

    fetchCameras()
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
        <h1 className="text-3xl font-bold text-gray-900">Câmeras</h1>
        <p className="text-gray-500 mt-1">Gerenciamento de câmeras de monitoramento</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {cameras.length > 0 ? (
          cameras.map((camera) => (
            <div key={camera.id} className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden hover:shadow-md transition-shadow">
              <div className="h-48 bg-gray-100 flex items-center justify-center">
                {camera.thumbnail_url ? (
                  <img src={camera.thumbnail_url} alt={camera.name} className="w-full h-full object-cover" />
                ) : (
                  <Camera className="w-16 h-16 text-gray-300" />
                )}
              </div>
              <div className="p-4">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="font-semibold text-gray-900">{camera.name}</h3>
                  <div className="flex items-center gap-1">
                    <Circle 
                      className={`w-3 h-3 ${camera.status === "online" ? "fill-emerald-500 text-emerald-500" : "fill-red-500 text-red-500"}`}
                    />
                    <span className={`text-xs font-medium capitalize ${camera.status === "online" ? "text-emerald-600" : "text-red-600"}`}>
                      {camera.status}
                    </span>
                  </div>
                </div>
                <p className="text-sm text-gray-500">{camera.location || "Sem localização"}</p>
              </div>
            </div>
          ))
        ) : (
          <div className="col-span-full text-center py-16 text-gray-500">
            <Camera className="w-16 h-16 mx-auto mb-4 text-gray-300" />
            <h3 className="text-lg font-semibold">Nenhuma câmera encontrada</h3>
            <p>Adicione sua primeira câmera para começar.</p>
          </div>
        )}
      </div>
    </div>
  )
}

export default Cameras