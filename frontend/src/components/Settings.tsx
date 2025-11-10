// VMS/frontend/src/components/Settings.tsx
import React, { useState, useEffect } from "react"
import { Settings as SettingsIcon, Bell, Shield, Loader2, AlertCircle } from 'lucide-react'
import { api } from "../lib/api"
import toast from "react-hot-toast"

// Interface para os dados de Configurações da API
// Baseado em VMS/backend/apps/configuracoes/serializers.py
interface SettingsData {
  notificacoes_habilitadas: boolean;
  email_suporte: string | null;
  em_manutencao: boolean;
}

const Settings: React.FC = () => {
  const [settings, setSettings] = useState<SettingsData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchSettings = async () => {
      setLoading(true)
      setError(null)
      try {
        // O endpoint é /api/settings/
        const data: SettingsData = await api.get("/settings/")
        setSettings(data)
      } catch (err: any) {
        setError("Falha ao carregar configurações.")
        toast.error("Falha ao carregar configurações.")
        console.error(err)
      } finally {
        setLoading(false)
      }
    }

    // Apenas admins podem carregar as configurações
    const userDataString = localStorage.getItem("gt_vision_user")
    const currentUser = userDataString ? JSON.parse(userDataString) : null
    if (currentUser?.role === 'admin') {
      fetchSettings()
    } else {
      setLoading(false)
      // Ocultamos o erro, pois viewers não deveriam nem ver esta página
    }
  }, [])
  
  // Função para salvar uma configuração
  const handleSettingChange = async (key: keyof SettingsData, value: any) => {
    if (!settings) return

    // Atualiza o estado local otimistamente
    const oldSettings = settings
    const newSettings = { ...settings, [key]: value }
    setSettings(newSettings)
    
    try {
      // Envia o PATCH para o backend
      // O endpoint é /api/settings/
      const updatedData = await api.patch("/settings/", { [key]: value })
      // Sincroniza o estado com a resposta do servidor
      setSettings(updatedData)
      toast.success("Configuração salva!")
    } catch (err: any) {
      // Reverte em caso de erro
      setSettings(oldSettings)
      toast.error(`Falha ao salvar: ${err.message}`)
    }
  }

  if (loading) {
    return (
      <div className="p-8 flex items-center justify-center h-full">
        <Loader2 className="w-12 h-12 text-blue-800 animate-spin" />
      </div>
    )
  }

  if (error || !settings) {
    return (
      <div className="p-8 flex flex-col items-center justify-center h-full text-red-600">
        <AlertCircle className="w-12 h-12 mb-4" />
        <h2 className="text-xl font-semibold">Erro ao carregar</h2>
        <p>{error || "Não foi possível carregar as configurações."}</p>
      </div>
    )
  }

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Configurações</h1>
        <p className="text-gray-500 mt-1">Preferências e configurações do sistema</p>
      </div>

      <div className="space-y-6 max-w-2xl">
        {/* Notifications */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
              <Bell className="w-5 h-5 text-blue-800" />
            </div>
            <h2 className="text-lg font-semibold text-gray-900">Notificações</h2>
          </div>
          <div className="flex items-center justify-between">
            <p className="text-sm text-gray-600">Receber notificações do sistema</p>
            <label className="relative inline-flex items-center cursor-pointer">
              <input 
                type="checkbox" 
                checked={settings.notificacoes_habilitadas} 
                className="sr-only peer" 
                onChange={(e) => handleSettingChange('notificacoes_habilitadas', e.target.checked)}
              />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-800"></div>
            </label>
          </div>
        </div>

        {/* Maintenance Mode */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-10 h-10 bg-red-100 rounded-lg flex items-center justify-center">
              <Shield className="w-5 h-5 text-red-600" />
            </div>
            <h2 className="text-lg font-semibold text-gray-900">Modo Manutenção</h2>
          </div>
          <div className="flex items-center justify-between">
            <p className="text-sm text-gray-600">Colocar o sistema em manutenção</p>
            <label className="relative inline-flex items-center cursor-pointer">
              <input 
                type="checkbox" 
                checked={settings.em_manutencao} 
                className="sr-only peer" 
                onChange={(e) => handleSettingChange('em_manutencao', e.target.checked)}
              />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-800"></div>
            </label>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Settings