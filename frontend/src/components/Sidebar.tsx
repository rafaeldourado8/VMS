// VMS/frontend/src/components/Sidebar.tsx
import React from "react"
import {LayoutDashboard, Camera, Target, BarChart3, LifeBuoy, Users, Settings, LogOut} from 'lucide-react'
import { useNavigate } from "react-router-dom"
import toast from "react-hot-toast"
import { api } from "../lib/api" // Importa o cliente de API

interface SidebarProps {
  currentPage: string
  setCurrentPage: (page: string) => void
  setIsAuthenticated: (value: boolean) => void
}

const Sidebar: React.FC<SidebarProps> = ({ currentPage, setCurrentPage, setIsAuthenticated }) => {
  const navigate = useNavigate()
  
  const userDataString = localStorage.getItem("gt_vision_user")
  const userData = userDataString ? JSON.parse(userDataString) : null

  // Define os itens do menu baseados na 'role' do usuário
  const menuItems = [
    { id: "dashboard", label: "Dashboard", icon: LayoutDashboard, roles: ["admin", "viewer"] },
    { id: "cameras", label: "Câmeras", icon: Camera, roles: ["admin", "viewer"] },
    { id: "detections", label: "Detecções", icon: Target, roles: ["admin", "viewer"] },
    { id: "analytics", label: "Analíticos", icon: BarChart3, roles: ["admin", "viewer"] },
    { id: "support", label: "Suporte", icon: LifeBuoy, roles: ["admin", "viewer"] },
    // Apenas admin pode ver Usuários e Configurações
    { id: "users", label: "Usuários", icon: Users, roles: ["admin"] },
    { id: "settings", label: "Configurações", icon: Settings, roles: ["admin"] },
  ]

  // Filtra o menu baseado na role do usuário
  const accessibleMenuItems = menuItems.filter(item => 
    userData?.role && item.roles.includes(userData.role)
  )

  const handleLogout = async () => {
    const refreshToken = localStorage.getItem("gt_vision_refresh_token")
    
    try {
      // Tenta fazer o logout no backend para invalidar o refresh token
      // O endpoint é /api/auth/logout/
      if (refreshToken) {
        await api.post("/auth/logout/", { refresh_token: refreshToken })
      }
    } catch (error) {
      console.error("Falha ao invalidar token no backend:", error)
      // Continua o logout no frontend de qualquer maneira
    } finally {
      // Limpa o localStorage
      localStorage.removeItem("gt_vision_token")
      localStorage.removeItem("gt_vision_refresh_token")
      localStorage.removeItem("gt_vision_user")
      
      // Atualiza o estado de autenticação e navega
      setIsAuthenticated(false)
      toast.success("Logout realizado com sucesso")
      navigate("/login")
    }
  }

  const getInitials = (name: string) => {
    return name
      .split(" ")
      .map(n => n[0])
      .join("")
      .toUpperCase()
      .slice(0, 2)
  }

  return (
    <aside className="w-64 bg-white border-r border-gray-200 flex flex-col">
      {/* Logo */}
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-blue-800 rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-lg">GT</span>
          </div>
          <div>
            <h1 className="font-bold text-gray-900 text-lg">GT Vision</h1>
            <p className="text-xs text-gray-500">Monitoramento</p>
          </div>
        </div>
      </div>

      {/* Navigation Menu */}
      <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
        {accessibleMenuItems.map((item) => {
          const Icon = item.icon
          const isActive = currentPage === item.id
          
          return (
            <button
              key={item.id}
              onClick={() => setCurrentPage(item.id)}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all ${
                isActive
                  ? "bg-blue-50 text-blue-800 font-medium"
                  : "text-gray-600 hover:bg-gray-50 hover:text-gray-900"
              }`}
            >
              <Icon className="w-5 h-5" />
              <span className="text-sm">{item.label}</span>
            </button>
          )
        })}
      </nav>

      {/* User Profile Footer */}
      <div className="p-4 border-t border-gray-200">
        <div className="flex items-center gap-3 mb-3">
          <div className="w-10 h-10 bg-emerald-500 rounded-full flex items-center justify-center">
            <span className="text-white font-semibold text-sm">
              {userData?.name ? getInitials(userData.name) : "AD"}
            </span>
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-gray-900 truncate">
              {userData?.name || "Admin"}
            </p>
            <p className="text-xs text-gray-500 truncate">
              {userData?.email || "admin@gtvision.com"}
            </p>
            <p className="text-xs text-emerald-600 font-medium capitalize">
              {userData?.role || "Admin"}
            </p>
          </div>
        </div>
        
        <button
          onClick={handleLogout}
          className="w-full flex items-center gap-2 px-4 py-2 text-sm text-red-600 hover:bg-red-50 rounded-lg transition-colors"
        >
          <LogOut className="w-4 h-4" />
          <span>Sair</span>
        </button>
      </div>
    </aside>
  )
}

export default Sidebar