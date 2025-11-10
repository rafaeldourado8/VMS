// frontend/src/pages/Cameras.tsx
import React, { useEffect, useState } from "react"
import toast, { Toaster } from "react-hot-toast"
import { api } from "../lib/api" // ajuste caminho se necessário
import { Plus, RefreshCw, Trash2, Edit2 } from "lucide-react"

type Camera = {
  id: number
  name: string
  rtsp_url?: string | null
  description?: string | null
  is_active?: boolean
}

export default function CamerasPage() {
  const [cameras, setCameras] = useState<Camera[]>([])
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [showModal, setShowModal] = useState(false)
  const [name, setName] = useState("")
  const [rtsp, setRtsp] = useState("")
  const [editingId, setEditingId] = useState<number | null>(null)

  const fetchCameras = async () => {
    setLoading(true)
    try {
      const res = await api.get("/cameras/") // espera array
      // Se api.get retorna objeto {data: ...} ajuste para res.data
      const data = Array.isArray(res) ? res : res?.data ?? res
      setCameras(data || [])
    } catch (err: any) {
      console.error("fetchCameras:", err)
      toast.error(err?.message || "Erro ao carregar câmeras")
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchCameras()
  }, [])

  const openAddModal = () => {
    setEditingId(null)
    setName("")
    setRtsp("")
    setShowModal(true)
  }

  const openEditModal = (cam: Camera) => {
    setEditingId(cam.id)
    setName(cam.name || "")
    setRtsp(cam.rtsp_url || "")
    setShowModal(true)
  }

  const handleSave = async () => {
    if (!name.trim()) return toast.error("Nome obrigatório")
    setSaving(true)
    try {
      if (editingId) {
        // editar
        await api.patch(`/cameras/${editingId}/`, { name: name.trim(), rtsp_url: rtsp || null })
        toast.success("Câmera atualizada")
      } else {
        // criar
        await api.post("/cameras/", { name: name.trim(), rtsp_url: rtsp || null })
        toast.success("Câmera adicionada")
      }
      setShowModal(false)
      fetchCameras()
    } catch (err: any) {
      console.error("handleSave:", err)
      toast.error(err?.message || "Falha ao salvar câmera")
    } finally {
      setSaving(false)
    }
  }

  const handleDelete = async (id: number) => {
    if (!confirm("Confirmar exclusão da câmera?")) return
    try {
      await api.delete(`/cameras/${id}/`)
      toast.success("Câmera excluída")
      fetchCameras()
    } catch (err: any) {
      console.error("handleDelete:", err)
      toast.error(err?.message || "Falha ao excluir câmera")
    }
  }

  return (
    <div className="p-8">
      <Toaster position="top-right" />
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold">Câmeras</h1>
          <p className="text-gray-500">Gerenciamento de câmeras de monitoramento</p>
        </div>
        <div className="flex items-center gap-2">
          <button
            className="inline-flex items-center gap-2 px-4 py-2 border rounded-lg text-sm hover:bg-gray-50"
            onClick={fetchCameras}
            disabled={loading}
            title="Atualizar"
          >
            <RefreshCw className="w-4 h-4" />
            {loading ? "Atualizando..." : "Atualizar"}
          </button>

          <button
            className="inline-flex items-center gap-2 px-4 py-2 bg-blue-800 text-white rounded-lg text-sm hover:bg-blue-900"
            onClick={openAddModal}
          >
            <Plus className="w-4 h-4" />
            Adicionar Câmera
          </button>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow-sm p-4">
        {loading ? (
          <div className="text-center py-12 text-gray-500">Carregando câmeras...</div>
        ) : cameras.length === 0 ? (
          <div className="text-center py-12 text-gray-400">
            <div className="mb-3 text-2xl">📷</div>
            <div className="font-medium">Nenhuma câmera encontrada</div>
            <div className="text-sm">Adicione sua primeira câmera para começar.</div>
          </div>
        ) : (
          <table className="w-full table-auto">
            <thead className="text-left text-sm text-gray-500 border-b">
              <tr>
                <th className="py-3 px-4">Nome</th>
                <th className="py-3 px-4">RTSP URL</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4 text-right">Ações</th>
              </tr>
            </thead>
            <tbody>
              {cameras.map((c) => (
                <tr key={c.id} className="border-b last:border-b-0">
                  <td className="py-3 px-4">{c.name}</td>
                  <td className="py-3 px-4 text-sm text-gray-600 truncate max-w-md">{c.rtsp_url || "—"}</td>
                  <td className="py-3 px-4">
                    {c.is_active ? <span className="text-green-600">Online</span> : <span className="text-gray-500">Offline</span>}
                  </td>
                  <td className="py-3 px-4 text-right">
                    <div className="inline-flex gap-2">
                      <button
                        className="px-3 py-1 border rounded-md text-sm hover:bg-gray-50 inline-flex items-center gap-2"
                        onClick={() => openEditModal(c)}
                        title="Editar"
                      >
                        <Edit2 className="w-4 h-4" />
                        Editar
                      </button>
                      <button
                        className="px-3 py-1 border rounded-md text-sm text-red-600 hover:bg-red-50 inline-flex items-center gap-2"
                        onClick={() => handleDelete(c.id)}
                        title="Excluir"
                      >
                        <Trash2 className="w-4 h-4" />
                        Excluir
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30">
          <div className="bg-white rounded-xl shadow-xl w-[720px] max-w-[95%] p-6">
            <h3 className="text-xl font-semibold mb-4">{editingId ? "Editar Câmera" : "Adicionar Câmera"}</h3>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1">Nome</label>
                <input
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="w-full border px-3 py-2 rounded-md"
                  placeholder="Nome da câmera"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">RTSP URL</label>
                <input
                  value={rtsp}
                  onChange={(e) => setRtsp(e.target.value)}
                  className="w-full border px-3 py-2 rounded-md"
                  placeholder="rtsp://..."
                />
                <p className="text-xs text-gray-500 mt-1">Opcional. Use apenas se sua câmera fornecer RTSP.</p>
              </div>
            </div>

            <div className="mt-6 flex justify-end gap-3">
              <button
                onClick={() => setShowModal(false)}
                className="px-4 py-2 border rounded-md text-sm bg-white hover:bg-gray-50"
                disabled={saving}
              >
                Cancelar
              </button>

              <button
                onClick={handleSave}
                className="px-4 py-2 bg-blue-800 text-white rounded-md text-sm hover:bg-blue-900 inline-flex items-center gap-2"
                disabled={saving}
              >
                {saving ? "Salvando..." : (editingId ? "Salvar alterações" : "Adicionar")}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}