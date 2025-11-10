// frontend/src/components/Cameras.tsx
import React, { useEffect, useMemo, useState } from "react"
import {
  Camera,
  Plus,
  RefreshCw,
  Trash2,
  Edit2,
  Loader2,
  AlertCircle,
  Zap,
  Calendar,
  Copy,
  CheckCircle,
  XCircle,
} from "lucide-react"
import { api } from "../lib/api"
import toast, { Toaster } from "react-hot-toast"

type CameraData = {
  id: number
  name: string
  location?: string | null
  status?: "online" | "offline"
  stream_url?: string | null
  thumbnail_url?: string | null
  is_active?: boolean
}

const PAGE_SIZE = 9

function normalizeResponse<T = any>(res: any): T {
  if (!res) return null as unknown as T
  if (Array.isArray(res)) return res as unknown as T
  return (res?.data ?? res) as T
}

export default function Cameras(): JSX.Element {
  const [cameras, setCameras] = useState<CameraData[]>([])
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [query, setQuery] = useState("")
  const [page, setPage] = useState(1)

  // modal states
  const [showModal, setShowModal] = useState(false)
  const [editing, setEditing] = useState<CameraData | null>(null)
  const [name, setName] = useState("")
  const [streamUrl, setStreamUrl] = useState("")
  const [location, setLocation] = useState("")
  const [details, setDetails] = useState<CameraData | null>(null)
  const [testingId, setTestingId] = useState<number | null>(null)
  const [snapshottingId, setSnapshottingId] = useState<number | null>(null)

  // role check (case-insensitive)
  const storedUser = typeof window !== "undefined" ? JSON.parse(localStorage.getItem("gt_vision_user") || "null") : null
  const isAdmin = !!(
    storedUser?.is_superuser ||
    (typeof storedUser?.role === "string" && storedUser.role.toLowerCase() === "admin")
  )

  useEffect(() => {
    fetchCameras()
  }, [])

  const fetchCameras = async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await api.get("/cameras/")
      const data = normalizeResponse<CameraData[]>(res) ?? []
      setCameras(data)
    } catch (err: any) {
      console.error("fetchCameras:", err)
      setError("Falha ao carregar câmeras")
      toast.error("Falha ao carregar câmeras")
    } finally {
      setLoading(false)
    }
  }

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase()
    if (!q) return cameras
    return cameras.filter((c) => (c.name || "").toLowerCase().includes(q) || (c.location || "").toLowerCase().includes(q) || (c.stream_url || "").toLowerCase().includes(q))
  }, [cameras, query])

  const pages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE))
  const visible = filtered.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE)

  const openAdd = () => {
    setEditing(null)
    setName("")
    setStreamUrl("")
    setLocation("")
    setShowModal(true)
  }

  const openEdit = (c: CameraData) => {
    setEditing(c)
    setName(c.name || "")
    setStreamUrl(c.stream_url || "")
    setLocation(c.location || "")
    setShowModal(true)
  }

  const openDetails = (c: CameraData) => {
    setDetails(c)
  }

  const handleSave = async () => {
    if (!name.trim()) {
      toast.error("Nome é obrigatório")
      return
    }
    setSaving(true)
    try {
      if (editing?.id) {
        await api.patch(`/cameras/${editing.id}/`, { name: name.trim(), stream_url: streamUrl || null, location: location || null })
        toast.success("Câmera atualizada")
      } else {
        await api.post("/cameras/", { name: name.trim(), stream_url: streamUrl || null, location: location || null })
        toast.success("Câmera criada")
      }
      setShowModal(false)
      fetchCameras()
    } catch (err: any) {
      console.error("handleSave:", err)
      toast.error(err?.message || "Erro ao salvar câmera")
    } finally {
      setSaving(false)
    }
  }

  const handleDelete = async (id: number) => {
    if (!confirm("Deseja realmente excluir esta câmera?")) return
    try {
      await api.delete(`/cameras/${id}/`)
      toast.success("Câmera excluída")
      fetchCameras()
    } catch (err: any) {
      console.error("handleDelete:", err)
      toast.error(err?.message || "Erro ao excluir câmera")
    }
  }

  const toggleActive = async (c: CameraData) => {
    try {
      const newState = !c.is_active
      // patch minimal
      await api.patch(`/cameras/${c.id}/`, { is_active: newState })
      toast.success(`Câmera ${newState ? "ativada" : "desativada"}`)
      // otimista: atualizar localmente
      setCameras((prev) => prev.map((p) => (p.id === c.id ? { ...p, is_active: newState } : p)))
    } catch (err: any) {
      console.error("toggleActive:", err)
      toast.error("Falha ao alterar estado")
    }
  }

  const testStream = async (id: number) => {
    setTestingId(id)
    try {
      // Ajuste o endpoint se o backend usar outro path
      await api.post(`/cameras/${id}/test-stream/`)
      toast.success("Teste de stream iniciado (ver logs do backend)")
    } catch (err: any) {
      console.error("testStream:", err)
      toast.error(err?.message || "Falha ao testar stream")
    } finally {
      setTestingId(null)
    }
  }

  const snapshot = async (id: number) => {
    setSnapshottingId(id)
    try {
      await api.post(`/cameras/${id}/snapshot/`)
      toast.success("Snapshot solicitado")
    } catch (err: any) {
      console.error("snapshot:", err)
      toast.error(err?.message || "Falha ao solicitar snapshot")
    } finally {
      setSnapshottingId(null)
    }
  }

  const copyRtsp = (rtsp?: string | null) => {
    if (!rtsp) return toast.error("RTSP não disponível")
    navigator.clipboard?.writeText(rtsp)
    toast.success("RTSP copiado")
  }

  return (
    <div className="p-8">
      <Toaster position="top-right" />
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold">Câmeras</h1>
          <p className="text-gray-500">Gerencie suas câmeras</p>
        </div>

        <div className="flex items-center gap-2">
          <div className="relative">
            <input
              value={query}
              onChange={(e) => { setQuery(e.target.value); setPage(1) }}
              placeholder="Buscar por nome, local ou stream..."
              className="px-4 py-2 border rounded-lg w-64 text-sm"
            />
            {query && (
              <button onClick={() => setQuery("")} className="absolute right-2 top-1/2 -translate-y-1/2 text-gray-400">
                <XCircle className="w-4 h-4" />
              </button>
            )}
          </div>

          <button
            onClick={() => { fetchCameras(); toast.promise(fetchCameras(), { loading: 'Atualizando...', success: 'Atualizado', error: 'Falha' }) }}
            className="inline-flex items-center gap-2 px-4 py-2 border rounded-lg text-sm hover:bg-gray-50"
            title="Atualizar"
          >
            <RefreshCw className="w-4 h-4" />
            Atualizar
          </button>

          <button
            onClick={openAdd}
            className="inline-flex items-center gap-2 px-4 py-2 bg-blue-800 text-white rounded-lg text-sm hover:bg-blue-900"
          >
            <Plus className="w-4 h-4" />
            Adicionar
          </button>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow-sm p-6">
        {loading ? (
          <div className="p-12 flex items-center justify-center">
            <Loader2 className="w-12 h-12 text-blue-800 animate-spin" />
          </div>
        ) : cameras.length === 0 ? (
          <div className="text-center py-16 text-gray-500">
            <Camera className="w-16 h-16 mx-auto mb-4 text-gray-300" />
            <h3 className="text-lg font-semibold">Nenhuma câmera encontrada</h3>
            <p className="mt-2">Adicione sua primeira câmera para começar.</p>
            <div className="mt-4">
              <button onClick={openAdd} className="px-4 py-2 bg-blue-800 text-white rounded-md">Adicionar Câmera</button>
            </div>
          </div>
        ) : (
          <>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
              {visible.map((cam) => (
                <div key={cam.id} className="bg-gray-50 rounded-xl border border-gray-200 overflow-hidden shadow-sm">
                  <div className="h-44 bg-gray-100 flex items-center justify-center">
                    {cam.thumbnail_url ? (
                      <img src={cam.thumbnail_url} alt={cam.name} className="w-full h-full object-cover" />
                    ) : (
                      <Camera className="w-16 h-16 text-gray-300" />
                    )}
                  </div>

                  <div className="p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="font-semibold text-gray-900">{cam.name}</h3>
                        <p className="text-xs text-gray-500">{cam.location || "Sem localização"}</p>
                      </div>

                      <div className="text-right">
                        <span className={`px-2 py-1 text-xs rounded-full font-medium ${cam.is_active ? "bg-emerald-100 text-emerald-700" : "bg-gray-100 text-gray-600"}`}>
                          {cam.is_active ? "Ativa" : "Inativa"}
                        </span>
                      </div>
                    </div>

                    <p className="mt-3 text-sm text-gray-600 truncate">{cam.stream_url || "RTSP não configurado"}</p>

                    <div className="mt-4 flex items-center justify-between gap-2">
                      <div className="flex gap-2">
                        <button onClick={() => openDetails(cam)} className="px-3 py-1 border rounded-md text-sm inline-flex items-center gap-2">
                          <Calendar className="w-4 h-4" />Detalhes
                        </button>

                        <button onClick={() => copyRtsp(cam.stream_url)} className="px-3 py-1 border rounded-md text-sm inline-flex items-center gap-2">
                          <Copy className="w-4 h-4" />Copiar RTSP
                        </button>
                      </div>

                      <div className="flex gap-2">
                        <button
                          onClick={() => toggleActive(cam)}
                          className={`px-3 py-1 text-sm rounded-md inline-flex items-center gap-2 ${cam.is_active ? "bg-white border" : "bg-emerald-600 text-white"}`}
                          title={cam.is_active ? "Desativar câmera" : "Ativar câmera"}
                        >
                          <CheckCircle className="w-4 h-4" />
                          {cam.is_active ? "Desativar" : "Ativar"}
                        </button>

                        <button onClick={() => openEdit(cam)} className="px-3 py-1 border rounded-md text-sm inline-flex items-center gap-2">
                          <Edit2 className="w-4 h-4" />Editar
                        </button>

                        <button onClick={() => handleDelete(cam.id)} className="px-3 py-1 border rounded-md text-sm text-red-600 inline-flex items-center gap-2">
                          <Trash2 className="w-4 h-4" />Excluir
                        </button>
                      </div>
                    </div>

                    <div className="mt-3 flex items-center justify-between gap-2">
                      <div className="text-xs text-gray-400">
                        Status: <span className="capitalize">{cam.status ?? "offline"}</span>
                      </div>

                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => testStream(cam.id)}
                          className="px-3 py-1 border rounded-md text-sm inline-flex items-center gap-2"
                          disabled={testingId === cam.id}
                        >
                          <Zap className="w-4 h-4" />
                          {testingId === cam.id ? "Testando..." : "Testar Stream"}
                        </button>

                        <button
                          onClick={() => snapshot(cam.id)}
                          className="px-3 py-1 border rounded-md text-sm inline-flex items-center gap-2"
                          disabled={snapshottingId === cam.id}
                        >
                          <Camera className="w-4 h-4" />
                          {snapshottingId === cam.id ? "Solicitando..." : "Snapshot"}
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Pagination */}
            <div className="mt-6 flex items-center justify-between">
              <div className="text-sm text-gray-500">{filtered.length} resultado(s)</div>
              <div className="flex items-center gap-2">
                <button onClick={() => setPage((p) => Math.max(1, p - 1))} disabled={page <= 1} className="px-3 py-1 border rounded-md">Anterior</button>
                <div className="px-3 py-1 border rounded-md text-sm bg-white">Pág {page}/{pages}</div>
                <button onClick={() => setPage((p) => Math.min(pages, p + 1))} disabled={page >= pages} className="px-3 py-1 border rounded-md">Próxima</button>
              </div>
            </div>
          </>
        )}
      </div>

      {/* Add/Edit Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30 p-4">
          <div className="bg-white rounded-xl shadow-xl w-[720px] max-w-[95%] p-6">
            <h3 className="text-xl font-semibold mb-4">{editing ? "Editar Câmera" : "Adicionar Câmera"}</h3>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1">Nome</label>
                <input value={name} onChange={(e) => setName(e.target.value)} className="w-full border px-3 py-2 rounded-md" placeholder="Nome da câmera" />
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">Stream URL</label>
                <input value={streamUrl} onChange={(e) => setStreamUrl(e.target.value)} className="w-full border px-3 py-2 rounded-md" placeholder="rtsp://..." />
                <p className="text-xs text-gray-500 mt-1">Opcional. Use apenas se sua câmera fornecer RTSP.</p>
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">Localização</label>
                <input value={location} onChange={(e) => setLocation(e.target.value)} className="w-full border px-3 py-2 rounded-md" placeholder="Endereço, sala, etc." />
              </div>
            </div>

            <div className="mt-6 flex justify-end gap-3">
              <button onClick={() => setShowModal(false)} className="px-4 py-2 border rounded-md text-sm bg-white hover:bg-gray-50" disabled={saving}>Cancelar</button>
              <button onClick={handleSave} className="px-4 py-2 bg-blue-800 text-white rounded-md text-sm hover:bg-blue-900" disabled={saving}>
                {saving ? "Salvando..." : (editing ? "Salvar" : "Adicionar")}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Details drawer/modal */}
      {details && (
        <div className="fixed inset-0 z-50 flex items-end sm:items-center justify-center bg-black/30 p-4">
          <div className="bg-white rounded-xl shadow-xl w-full sm:w-[720px] max-w-[95%] p-6">
            <div className="flex items-start justify-between">
              <div>
                <h3 className="text-xl font-semibold">{details.name}</h3>
                <p className="text-sm text-gray-500">{details.location}</p>
              </div>
              <div className="flex items-center gap-2">
                <button onClick={() => copyRtsp(details.stream_url)} className="px-3 py-1 border rounded-md inline-flex items-center gap-2">
                  <Copy className="w-4 h-4" />Copiar RTSP
                </button>
                <button onClick={() => setDetails(null)} className="px-3 py-1 border rounded-md">Fechar</button>
              </div>
            </div>

            <div className="mt-4">
              <p className="text-sm text-gray-600">Status: <span className="capitalize">{details.status ?? "offline"}</span></p>
              <p className="text-sm text-gray-600 mt-2">Stream: {details.stream_url || "—"}</p>
              <div className="mt-4">
                {details.thumbnail_url ? <img src={details.thumbnail_url} alt="thumb" className="w-full rounded" /> : (
                  <div className="h-48 bg-gray-100 flex items-center justify-center rounded">
                    <Camera className="w-12 h-12 text-gray-300" />
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}