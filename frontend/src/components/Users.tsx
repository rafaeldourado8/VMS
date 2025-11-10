// VMS/frontend/src/components/Users.tsx
import React, { useState, useEffect } from "react"
import { Users as UsersIcon, Circle, Loader2, AlertCircle, ShieldQuestion } from 'lucide-react'
import { api } from "../lib/api"
import toast from "react-hot-toast"

// Interface para os dados do Usuário da API
// Baseado em VMS/backend/apps/usuarios/serializers.py
interface UserData {
  id: number;
  name: string;
  email: string;
  role: "admin" | "viewer";
  is_active: boolean;
  created_at: string;
}

const Users: React.FC = () => {
  const [users, setUsers] = useState<UserData[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  
  // Apenas admins podem ver esta página (check do Sidebar), mas fazemos
  // uma verificação de segurança no 'role' do usuário logado.
  const userDataString = localStorage.getItem("gt_vision_user")
  const currentUser = userDataString ? JSON.parse(userDataString) : null
  const isAdmin = currentUser?.role === 'admin'

  useEffect(() => {
    if (!isAdmin) {
      setError("Acesso negado. Você precisa ser administrador.")
      setLoading(false)
      return
    }

    const fetchUsers = async () => {
      setLoading(true)
      setError(null)
      try {
        // O endpoint é /api/users/
        const data: UserData[] = await api.get("/users/")
        setUsers(data)
      } catch (err: any) {
        setError("Falha ao carregar usuários.")
        toast.error("Falha ao carregar usuários.")
        console.error(err)
      } finally {
        setLoading(false)
      }
    }

    fetchUsers()
  }, [isAdmin])


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
  
  if (!isAdmin) {
      return (
      <div className="p-8 flex flex-col items-center justify-center h-full text-orange-600">
        <ShieldQuestion className="w-12 h-12 mb-4" />
        <h2 className="text-xl font-semibold">Acesso Negado</h2>
        <p>Você não tem permissão para ver esta página.</p>
      </div>
    )
  }

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Usuários</h1>
        <p className="text-gray-500 mt-1">Gerenciamento de usuários do sistema</p>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-200">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="px-6 py-4 text-left text-xs font-medium text-gray-600 uppercase">Nome</th>
                <th className="px-6 py-4 text-left text-xs font-medium text-gray-600 uppercase">Email</th>
                <th className="px-6 py-4 text-left text-xs font-medium text-gray-600 uppercase">Função</th>
                <th className="px-6 py-4 text-left text-xs font-medium text-gray-600 uppercase">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {users.map((user) => (
                <tr key={user.id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 bg-blue-800 rounded-full flex items-center justify-center">
                        <span className="text-white font-semibold text-sm">
                          {user.name.split(" ").map(n => n[0]).join("").toUpperCase().slice(0, 2)}
                        </span>
                      </div>
                      <span className="text-sm font-medium text-gray-900">{user.name}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-600">{user.email}</td>
                  <td className="px-6 py-4">
                    <span className="inline-flex px-3 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded-full capitalize">
                      {user.role}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-2">
                      <Circle 
                        className={`w-3 h-3 ${user.is_active ? "fill-emerald-500 text-emerald-500" : "fill-gray-400 text-gray-400"}`}
                      />
                      <span className={`text-sm ${user.is_active ? "text-emerald-600" : "text-gray-500"}`}>
                        {user.is_active ? "Ativo" : "Inativo"}
                      </span>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

export default Users